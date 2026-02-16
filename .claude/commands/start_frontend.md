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
5. Modify the file `_ext/pool.psychoinformatics.de-ui/dist/config.yaml`: set the `service_base_url` key to the following value:
   ```yaml
   service_base_url:
     - url: http://localhost:8111/research_info/
       type: write
   ```
6. Serve the frontend (this command is blocking):
   ```
   hatch run tools:serve-frontend
   ```
   The frontend will be available at http://localhost:8000.
