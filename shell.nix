{ pkgs ? import <nixpkgs> {} }:

let
  python = pkgs.python3; # or pkgs.python311, pkgs.python312, etc.
  venvDir = ".venv";
  libcppPath = "${pkgs.stdenv.cc}/lib";
  lib-path = with pkgs; lib.makeLibraryPath [
    stdenv.cc.cc
  ];
in
pkgs.mkShell {
  buildInputs = [
      python
  ];

  shellHook = ''
    # Set up a virtual environment if it doesn't exist
    SOURCE_DATE_EPOCH=$(date +%s)
    export "LD_LIBRARY_PATH=$LD_LIBRARY_PATH:${lib-path}"
    if [ ! -d "${venvDir}" ]; then
      echo "Adding ${libcppPath} to LD_LIBRARY_PATH"
      echo "Creating virtual environment in ${venvDir}..."
      ${python}/bin/python -m venv ${venvDir}
      source ${venvDir}/bin/activate
      echo "Installing packages into venv..."
    else
      # If venv exists, just activate it
      echo "Activating virtual environment in ${venvDir}..."
      source ${venvDir}/bin/activate
    fi
  '';
}
