{
  bndry.skills.enable = true;

  home = {
    homeDirectory = "/tmp/bndry-skills-home-manager-test";
    stateVersion = "26.05";
    username = "bndry-skills-test";
  };

  programs.agent-skills = {
    enable = true;
    sources.project = {
      path = ../skills;
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
