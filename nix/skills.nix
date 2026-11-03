{
  pkgs,
  self,
}: {
  source = {
    path = self;
    subdir = "skills";
    filter.maxDepth = 1;
  };

  definitions = {
    bndry-custom-fields-schema = {
      from = "bndry";
      path = "bndry-custom-fields-schema";
      packages = [
        pkgs.jq
        pkgs.python3
      ];
      rewriteCommands = false;
      targets = [
        "agents"
        "claude"
      ];
    };

    bndry-formkit-schema = {
      from = "bndry";
      path = "bndry-formkit-schema";
      packages = [pkgs.python3];
      rewriteCommands = false;
      targets = [
        "agents"
        "claude"
      ];
    };
  };
}
