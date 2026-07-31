Launch the local frontend web UI for the dump-things-server.

## Steps

1. Check if the directory `_ext/pool.psychoinformatics.de-ui/` exists in the project root. If it does, skip to step 6.
2. Clone the frontend repo:
   ```
   git clone https://hub.psychoinformatics.de/www/pool.psychoinformatics.de-ui _ext/pool.psychoinformatics.de-ui
   ```
3. Fetch all submodules within the cloned repo:
   ```
   cd _ext/pool.psychoinformatics.de-ui && git submodule update --init --recursive
   ```
4. Build the frontend:
   ```
   cd _ext/pool.psychoinformatics.de-ui && make install && make
   ```
5. The build produces two application variants, each in its own
   subdirectory of `dist/` with its own copy of the configuration:
   - `dist/ui/`: the main knowledge pooling tool
   - `dist/kickstarter/`: the "knowledge kickstarter" variant

   In **both** `_ext/pool.psychoinformatics.de-ui/dist/ui/config.yaml` and
   `_ext/pool.psychoinformatics.de-ui/dist/kickstarter/config.yaml`, replace
   the `service_base_url` key (which by default lists the production
   `pool.psychoinformatics.de` endpoints) with the following value:
   ```yaml
   service_base_url:
     - url: http://localhost:8111/research_info/
       type: write
   ```
6. Serve the frontend (this command is blocking):
   ```
   hatch run tools:serve-frontend
   ```
   This serves the whole `dist/` directory, so that both variants are
   reachable under their own subpaths, mirroring the layout of the
   production deployment at https://pool.psychoinformatics.de/:
   - http://localhost:8000/ui/
   - http://localhost:8000/kickstarter/

   Note that there is no application at the server root
   (http://localhost:8000/); it only lists the two subdirectories.
