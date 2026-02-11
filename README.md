# dump-research-info

-----

This repo provides a setup to gather research information related to 
Center for Open Neuroscience (CON) as (meta)data and a tool to dump the gathered 
(meta)data to an instance of [dump-things-server](https://hub.psychoinformatics.de/inm7/dump-things-server).
The (meta)data gathered must conform to the data models defined in the 
[demo-research-information-schema](https://concepts.datalad.org/s/demo-research-information/unreleased.yaml),
which is documented at [DataLad Concepts](https://concepts.datalad.org/s/demo-research-information/unreleased/),
and the dump-things-server instance receives the (meta)data in a collection that must
conform to the data models defined in the 
[demo-research-information-schema](https://concepts.datalad.org/s/demo-research-information/unreleased.yaml)
as well.

The setup is done in a way to facilitate AI coding agents, such as Claude Code, to gather
the (meta)data from various sources, such as CON related websites and project repositories,
and to validate the gathered (meta)data against the target data models through the
REST API of a dump-things-server instance. Once any gathered (meta)data is validated,
it will be added to this repository. The tool provided in this repository can be used
for dumping all the gathered (meta)data in this repo to a dump-things-server instance.

The gathered (meta)data are stored in separate JSON files each named with the name of
a model (or class) in the demo-research-information-schema, and the files are stored
in a subdirectory named after the source of the (meta)data. All (meta)data records of
a particular class from a particular source are stored in the file named after the class
in the subdirectory named after the source. All subdirectories are stored in the 
`data` directory in this repository.

## Table of Contents

- [License](#license)

## Installation

```console
pip install dump-research-info
```

## License

`dump-research-info` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
