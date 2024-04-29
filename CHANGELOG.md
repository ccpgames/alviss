# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [3.2.1] - 2024-04-29

### Changed

- Stubber now has an option to only "export" the resulting "Final" stub 
  class and keeping all the other stubs "private" and this option is True by
  default (they don't really need to be public)
- You can now give the resulting "Final" config stub a custom name
- You can also give the "Final" config stub an empty string for a name which 
  will simply omit generating it (for custom/complex composition of stubs 
  later on if people want)
- All stubs now also inherit from `dict` because any attribute in 
  `BaseConfig` that's a Map (and thus has a stub class) will also behave as 
  a `dict` (even if `Empty`)

### Fixed

- Stubber now appends an underscore to stubs with Python reserved keywords 
  like `class` and `def` etc.
- The `BaseConfig` object now also spots attribute fetching of those 
  keywords with an appended underscore and fetches the correct attribute 
  nevertheless.


## [3.2.0] - 2024-04-22

### Added

- Stub generators from descriptor config files where you structure out your 
  config file and give each value the Python type you expect the config to
  yield in order to generate type-hinting stub-classes that match the structure 
  of your config file(s).
- CLI commands for running the stub generation: `alviss-stubber`
- CLI commands for running the config rendering: `alviss-render`
- A bunch of Alviss specific Error Exceptions that are raised e.g. 
  when files aren't found or when Fidelius is required but isn't installed

### Changed

- The rendering of static single file configs from Alviss config files and 
  expressions has now been moved into its own sub-module with a standard API  


## [3.1.0] - 2024-04-12

### Added

- A way to make evaluating environment variables require a value to be found by 
  appending `!=` to the end of the expression like so `${__ENV__:API_KEY!=}`. 
  Missing values will trigger a `ValueError` raised when loading config files.

## [3.0.0] - 2024-04-11

### Added

- Fidelius mode - Alviss now reads the `ALVISS_FIDELIUS_MODE` environment 
  variable to determine one of these Fidelius modes available:
  - `ON_DEMAND` (**default**): Fidelius is only ever loaded (i.e. an import is 
    attempted) if fidelius expressions (`__FID__`) are encountered when reading 
    a config
  - `ENABLED`: Alviss tries to import fidelius on startup and raises an 
    `ImportError` if it fails
  - `DISABLED`: All fidelius expressions (`__FID__`) are simply ignored and 
    left unparsed
  - `SUBSTITUTE_ENV`: All fidelius expressions (`__FID__`) are treated as if 
    they are environment variable expressions (`__ENV__`)
  - `MOCK`: Fidelius will be initialised using its mock implementation, 
    which uses a singleton in-memory datastore, making this useful for testing
- Error reporting on the keys that have Fidelius tags in them in case of a 
  Fidelius related error _(like access problems or if fidelius is not installed)_
- Fidelius can now grab config values from the config files Alviss is 
  reading via the `__fidelius__` special key (e.g. `ALVISS_FIDELIUS_MODE` 
  and any `kwargs` that `AwsParamStoreRepo` takes.

### Changed

- Migrated the project from our internal repos to Github and Pypi
- Alviss now ships by default without [fidelius](https://pypi.org/project/fidelius/)
  support and runs in `ALVISS_FIDELIUS_MODE=ON_DEMAND` and this only tries 
  to import fidelius if a `__FID__` expression is encountered
  - Installing Alviss with built in fidelius support can still be done via 
    `pip install alviss[fidelius]` plus all the `boto3` stuff and such
- Bumped the `fidelius` version to 1.0.0 so now all the new environment 
  variables available in that version can be used to configure fidelius in 
  Alviss, e.g. by setting `FIDELIUS_AWS_ENDPOINT_URL` to point to a 
  [LocalStack](https://github.com/localstack/localstack) container for testing 
  and/or development.

### Fixed

- An issue where the default values of environment variables could not 
  contain any whitespaces (like a simple space)


## [2.7.1] - 2021-11-30

### Fixed

- Issue where Fidelius expressions were being evaluated by default when calling `render_load`


## [2.6.0] - 2021-11-29

### Added

- Automatic parsing of Fidelius expressions `{$__FID__:...}`


## [2.5.0] - 2021-08-21

### Changed

- Environment variable injection tags can now have a default value that they 
  get assigned if the environment variable in question was not found 
  - E.g. `app_version: ${__ENV__:APP_VERSION=0.0.0}` where `app_version` 
    will be `0.0.0` if `APP_VERSION` is not found on the system as an 
    environment variable)


## [2.4.0] - 2021-07-29

### Fixed

- A rare but serious error where nested internal referencing with multiple 
  variables would break prematurely in files that extend others with the same 
  keys


## [2.3.0] - 2021-07-27

### Added

- The `raw_load` method that loads a config file and returns the raw 
  `dict` result
  - This is mainly intended to be used for debugging large and complex sets 
    of config files with multiple inclusions and extensions and internal 
    references and such, so that reading in the files and seeing the 
    resulting structure after everything has been included and evaluated can 
    help.
- The `render_load` method that loads a config file and returns the 
  rendered `str` result (JSON or YAML depending on the input file)
  - This is mainly intended to be used for debugging large and complex sets 
    of config files with multiple inclusions and extensions and internal 
    references and such, so that reading in the files and seeing the 
    resulting JSON or YAML after everything has been included and evaluated can 
    help, as if this was just one large file with static values.


## [2.2.0] - 2021-07-27

### Added

- The `unmaksed` param (default=`False`) to the `as_json`, `as_yaml` and 
  `as_dict` methods in order to use `alviss` to load and render config and 
  export as a single "compiled" file e.g. for deployment manifests and such


## [2.1.1] - 2021-07-26

### Fixed

- Issue with resolution order of extended keys with variables
- Issue with resolving variables in entries with nested keys collapsed into 
  one string


## [2.1.0] - 2021-07-26

### Added

- Support for multiple files in `__extends__` keys
- Support for nested `__extends__` keys
- Support for using `__extends__` and `__include__` in collapsed keys
- Aliases:
  - `__extend__` => `__extends__`
  - `__includes__` => `__include__`


## [2.0.0] - 2021-07-26

### Added

 - YAML support _(YAY! Now we can properly document/comment in config files!)_
 - New `quickloader` module
 - Support for extending base files via `__extends__` key
 - Support for including additional files via `__include__` key
 - Better config representation _(e.g. for logs)_ via `as_json()` and 
   `as_yaml()` methods
 - Internal reference variable resolving via `${keys}`
 - Support for collapsing multiple nested keys into a single key with dots 
   like so: `database.connection.host`
 - Support for documentation keys in JSON files via the "comment-like" 
   `__doc__` key
 - Way to "comment-out" any keys in JSON by ignoring any keys starting with 
   a double underscore.
 - Support for including environment variables into any value string, 
   wherever in that string

### Changed

- The format for environment variable inclusion to `${__ENV__:SOME_ENV_VAR}`
- Refactored structure _(just `from alviss.quickloader import *` and go)_

### Removed

- The singleton functionality of `BaseConfig` by default and moved it over to 
  `SingletonConfig`


## [1.3.0] - 2020-11-18

### Changed 

- The CI/CD pipelines


## [1.2.1] - 2019-07-19

### Changed 

- If something in config starts with "_", it's no longer printed


## [1.2.0] - 2019-07-11 

### Changed 

- Requirements and version bump due to bug in dependency


## [1.1.1] - 2019-05-21

### Fixed

- A bug from `typeutils.iters.nested_dict_update` that didn't
  update the nested parts of nested `EmptyDict`


## [1.1.0] - 2019-05-21

### Changed

- The `update` to use `nested_dict_update` from `typeutils` 2.5+ so
 config value updates can be updated safely in a nested way e.g. in
 order to have a base config file and then a much smaller override
 config file
- The `__str__` and `__repr__` and calls so they now mask out secrets and 
  passwords _(any keys with the following words in them: 'pass', 'key', 
  'secret', 'token')_


## [1.0.0] - 2019-02-20

Initial release

### Added

- Everything!
