# Local cross-provider test. Call with a private sibling checkout and
# representative generic/Claude-only skill names; no private source is pinned.
{
  bndrySkillsPath,
  llmClaudeOnlySkill,
  llmGenericSkill,
  llmRequiredCommand,
  llmSkillsPath,
}: let
  bndrySkills = builtins.getFlake "path:${toString bndrySkillsPath}";
  llmSkills = builtins.getFlake "path:${toString llmSkillsPath}";
  pkgs = import bndrySkills.inputs.nixpkgs {
    system = builtins.currentSystem;
    config.allowUnfree = true;
  };

  home = bndrySkills.inputs.home-manager.lib.homeManagerConfiguration {
    inherit pkgs;
    modules = [
      bndrySkills.homeModules.default
      llmSkills.homeModules.default
      {
        bndry.skills.enable = true;
        bndry.llm-skills = {
          enable = true;
          selected = [
            llmGenericSkill
            llmClaudeOnlySkill
          ];
        };

        home = {
          homeDirectory = "/tmp/bndry-skills-combined-test";
          stateVersion = "26.05";
          username = "bndry-skills-combined-test";
        };

        programs.agent-skills = {
          enable = true;
          sources.project = {
            path = bndrySkillsPath + "/skills";
            idPrefix = "project";
            filter.maxDepth = 1;
          };
          skills.enable = ["project/bndry-formkit-schema"];
          targets = {
            agents.enable = true;
            claude.enable = true;
          };
        };
      }
    ];
  };

  activation = home.config.home.activation;
  drivers = {
    bndryAgents = activation.bndry-skills-agents.data;
    bndryClaude = activation.bndry-skills-claude.data;
    llmAgents = activation.bndry-llm-skills-agents.data;
    llmClaude = activation.bndry-llm-skills-claude.data;
  };
in
  pkgs.runCommand "bndry-skills-combined-home-manager-test" {} ''
    export PATH=${home.config.home.path}/bin
    command -v jq >/dev/null
    command -v python3 >/dev/null
    command -v ${pkgs.lib.escapeShellArg llmRequiredCommand} >/dev/null

    assert_agents() {
      test -f "$HOME/.agents/skills/bndry-custom-fields-schema/SKILL.md"
      test -f "$HOME/.agents/skills/bndry-formkit-schema/SKILL.md"
      test -f "$HOME/.agents/skills/${llmGenericSkill}/SKILL.md"
      test ! -e "$HOME/.agents/skills/${llmClaudeOnlySkill}"
      test -f "$HOME/.agents/skills/project/bndry-formkit-schema/SKILL.md"
    }

    assert_claude() {
      test -f "$HOME/.claude/skills/bndry-custom-fields-schema/SKILL.md"
      test -f "$HOME/.claude/skills/bndry-formkit-schema/SKILL.md"
      test -f "$HOME/.claude/skills/${llmGenericSkill}/SKILL.md"
      test -f "$HOME/.claude/skills/${llmClaudeOnlySkill}/SKILL.md"
      test -f "$HOME/.claude/skills/project/bndry-formkit-schema/SKILL.md"
    }

    export HOME="$TMPDIR/llm-first"
    ${drivers.llmAgents}
    assert_agents
    ${drivers.bndryAgents}
    assert_agents
    ${drivers.llmClaude}
    assert_claude
    ${drivers.bndryClaude}
    assert_claude

    export HOME="$TMPDIR/bndry-first"
    ${drivers.bndryAgents}
    assert_agents
    ${drivers.llmAgents}
    assert_agents
    ${drivers.bndryClaude}
    assert_claude
    ${drivers.llmClaude}
    assert_claude

    ${pkgs.coreutils}/bin/touch "$out"
  ''
