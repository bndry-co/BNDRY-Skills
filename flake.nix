{
  description = "Public BNDRY Agent Skills catalog";

  inputs = {
    agent-skills = {
      url = "github:Kyure-A/agent-skills-nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    home-manager = {
      url = "github:nix-community/home-manager/release-26.05";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    systems.url = "github:nix-systems/default";
  };

  outputs = {
    agent-skills,
    home-manager,
    nixpkgs,
    self,
    systems,
    ...
  }: let
    eachSystem = nixpkgs.lib.genAttrs (import systems);
    providerFor = system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in
      import ./nix/provider.nix {
        inherit agent-skills pkgs self;
        lib = nixpkgs.lib;
      };
    packageFor = system: target: let
      provider = providerFor system;
    in
      provider.bundleFor {
        inherit target;
        definitions = provider.catalog.definitions;
      };
    module = import ./nix/home-manager.nix {inherit agent-skills self;};
  in {
    homeModules.default = module;
    homeManagerModules.default = module;

    packages = eachSystem (system: let
      agents = packageFor system "agents";
      claude = packageFor system "claude";
    in {
      default = agents;
      bndry-skills-agents = agents;
      bndry-skills-claude = claude;
    });

    checks = eachSystem (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      provider = providerFor system;
      agents = packageFor system "agents";
      claude = packageFor system "claude";
      claudeOnlyDefinitions =
        provider.catalog.definitions
        // {
          bndry-formkit-schema =
            provider.catalog.definitions.bndry-formkit-schema
            // {targets = ["claude"];};
        };
      routedAgents = provider.bundleFor {
        target = "agents";
        definitions = claudeOnlyDefinitions;
      };
      routedClaude = provider.bundleFor {
        target = "claude";
        definitions = claudeOnlyDefinitions;
      };
    in {
      bundles = pkgs.runCommand "check-bndry-skills-bundles" {} ''
        for bundle in ${agents} ${claude}; do
          test -f "$bundle/bndry-custom-fields-schema/SKILL.md"
          test -e "$bundle/bndry-custom-fields-schema/jq"
          test -e "$bundle/bndry-custom-fields-schema/python3"
          test -f "$bundle/bndry-formkit-schema/SKILL.md"
          test -e "$bundle/bndry-formkit-schema/python3"
        done

        test ! -e ${routedAgents}/bndry-formkit-schema
        test -f ${routedClaude}/bndry-formkit-schema/SKILL.md
        touch "$out"
      '';

      home-manager =
        (home-manager.lib.homeManagerConfiguration {
          inherit pkgs;
          modules = [
            module
            ./nix/test-home-manager.nix
          ];
        }).activationPackage;
    });
  };
}
