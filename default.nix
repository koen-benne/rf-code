{
  dream2nix,
  config,
  lib,
  ...
}: {
  imports = [
    dream2nix.modules.dream2nix.WIP-python-pyproject
  ];

  deps = {nixpkgs, ...}: {
    python = nixpkgs.python311;
    portaudio = nixpkgs.portaudio;
  };

  mkDerivation = {
    src = ./.;
  };

  # This is not strictly required, but setting it will keep most dependencies
  #   locked, even when new dependencies are added via pyproject.toml
  pip.pypiSnapshotDate = "2024-05-05";

  pip.overrides.pyaudio = {
    env.autoPatchelfIgnoreMissingDeps = true;
    mkDerivation.buildInputs = [
      config.deps.portaudio
    ];
  };
}
