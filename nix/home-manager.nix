{
  agent-skills,
  self,
}: {
  config,
  lib,
  pkgs,
  ...
}: let
  cfg = config.bndry.skills;
  provider = import ./provider.nix {inherit agent-skills lib pkgs self;};
  selected = provider.selectDefinitions cfg.selected;
  nativeCfg = config.programs.agent-skills;
  providerBundles = lib.genAttrs provider.targets (target:
    provider.bundleFor {
      inherit target;
      definitions = selected;
    });
  routeBundlesFor = target:
    lib.concatMap
    (bundles: lib.optional (bundles ? ${target}) bundles.${target})
    (builtins.attrValues config.bndry.agent-skills.internal.routeBundles);
  activeTargets =
    if nativeCfg.enable
    then
      agent-skills.lib.agent-skills.targetsFor {
        targets = lib.getAttrs provider.targets nativeCfg.targets;
        system = pkgs.stdenv.hostPlatform.system;
      }
    else {};

  route = target: targetConfig: let
    bundle = pkgs.symlinkJoin {
      name = "bndry-skills-${target}-with-native-sources";
      paths = [nativeCfg.bundlePath] ++ routeBundlesFor target;
    };
    programName = "bndry-skills-install-${target}";
    syncProgram = agent-skills.lib.agent-skills.mkSyncProgram {
      inherit bundle pkgs programName;
      targets.${target} = targetConfig;
      system = pkgs.stdenv.hostPlatform.system;
      excludePatterns = nativeCfg.excludePatterns;
    };
  in
    lib.nameValuePair "bndry-skills-${target}" (lib.hm.dag.entryAfter ["agent-skills"] ''
      ${syncProgram}/bin/${programName}
    '');
in {
  imports = [
    {
      _file = "bndry-agent-skills/upstream-home-manager";
      key = "bndry-agent-skills/upstream-home-manager";
      imports = [agent-skills.homeManagerModules.default];
    }
  ];

  options.bndry.skills = {
    enable = lib.mkEnableOption "BNDRY's public Agent Skills catalog";

    selected = lib.mkOption {
      type = lib.types.listOf (lib.types.enum provider.skillNames);
      default = provider.skillNames;
      description = "Public BNDRY skills to install; defaults to the complete catalog.";
    };
  };

  options.bndry.agent-skills.internal.routeBundles.bndry-skills = lib.mkOption {
    type = lib.types.attrsOf lib.types.package;
    default = {};
    internal = true;
    description = "BNDRY Skills bundles grouped by inferred installation target.";
  };

  config = lib.mkIf cfg.enable {
    warnings = lib.optional (!nativeCfg.enable) ''
      bndry-skills: the provider is enabled, but programs.agent-skills.enable is false; no skills will be installed.
    '';

    home.packages = provider.packagesFor selected;

    bndry.agent-skills.internal.routeBundles.bndry-skills = providerBundles;

    home.activation = lib.mapAttrs' route activeTargets;
  };
}
