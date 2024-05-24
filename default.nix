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
    ffmpeg = nixpkgs.ffmpeg;
  };

  mkDerivation = {
    src = ./.;
    nativeBuildInputs = [config.deps.ffmpeg];
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
  pip.overrides.ffmpeg-audio = {
    env.autoPatchelfIgnoreMissingDeps = true;
    mkDerivation.buildInputs = [
      config.deps.ffmpeg
    ];
  };
}
