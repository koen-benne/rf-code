{
  dream2nix,
  config,
  lib,
  ...
}: let
  pyproject = lib.importTOML ./matchcenterai/pyproject.toml;
  buildWithSetuptools = {
    buildPythonPackage.format = "pyproject";
    mkDerivation.buildInputs = [config.deps.python.pkgs.setuptools config.deps.python.pkgs.setuptools-scm];
  };
in {
  imports = [
    dream2nix.modules.dream2nix.pip
    buildWithSetuptools
  ];

  deps = {nixpkgs, ...}: {
    python = nixpkgs.python311;
    portaudio = nixpkgs.portaudio;
    ffmpeg = nixpkgs.ffmpeg;
    flac = nixpkgs.flac;
    curl = nixpkgs.curl;
    wget = nixpkgs.wget;
  };

  inherit (pyproject.project) name version;

  mkDerivation = {
    src = lib.concatStringsSep "/" [
      config.paths.projectRoot
      config.paths.package
      "matchcenterai"
    ];
    nativeBuildInputs = [config.deps.ffmpeg config.deps.flac config.deps.curl config.deps.wget];
    propagatedBuildInputs = [
      config.deps.ffmpeg
      config.deps.curl
      config.deps.wget
    ];
  };

  buildPythonPackage.pythonImportsCheck = [
    "blogger"
    "summarizer"
  ];

  pip = {
    pypiSnapshotDate = "2024-05-05";
    requirementsList = [
      "${config.paths.package}/matchcenterai"
      "${config.paths.package}/blogger"
      "${config.paths.package}/summarizer"
    ];

    overrides = {
      pyaudio = {
        env.autoPatchelfIgnoreMissingDeps = true;
        mkDerivation.buildInputs = [
          config.deps.portaudio
        ];
      };
      ffmpeg-audio = {
        env.autoPatchelfIgnoreMissingDeps = true;
        mkDerivation.buildInputs = [
          config.deps.ffmpeg
        ];
      };
      blogger = buildWithSetuptools;
      summarizer = buildWithSetuptools;
    };
  };
}
