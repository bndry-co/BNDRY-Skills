{
  agent-skills,
  lib,
  pkgs,
  self,
}: let
  agentLib = agent-skills.lib.agent-skills;
  catalog = import ./skills.nix {inherit pkgs self;};
  skillNames = builtins.attrNames catalog.definitions;

  selectDefinitions = names: lib.getAttrs names catalog.definitions;
  definitionsFor = target: definitions:
    lib.mapAttrs
    (_: definition: builtins.removeAttrs definition ["targets"])
    (lib.filterAttrs (_: definition: builtins.elem target definition.targets) definitions);

  selectionFor = target: definitions:
    agentLib.selectSkills {
      catalog = {};
      sources.bndry = catalog.source;
      skills = definitionsFor target definitions;
    };
in {
  inherit catalog skillNames selectDefinitions;

  targets = lib.unique (lib.concatMap (name: catalog.definitions.${name}.targets) skillNames);

  packagesFor = definitions:
    builtins.map
    (package:
      if package == pkgs.python3
      then lib.lowPrio package
      else package)
    (lib.unique (lib.concatMap (definition: definition.packages or []) (builtins.attrValues definitions)));

  bundleFor = {
    definitions,
    target,
  }:
    agentLib.mkBundle {
      inherit pkgs;
      name = "bndry-skills-${target}";
      selection = selectionFor target definitions;
    };
}
