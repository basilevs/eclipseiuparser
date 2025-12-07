# Install
```
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install eclipseiuparser@git+https://github.com/basilevs/eclipseiuparser.git
```

# Definitions
Unit can be bundle, feature or product (from "installation unit", a P2 term)

# Use

Navigate to your Eclipse Platform application sources:

```
$ cd ~/git/<my_application>
```

## Where

`where <plugin_id>` prints a list of features including a plugin:

```
$ command where org.eclipse.pde.core
feature:org.eclipse.rcptt.runner.headless 	 runner/features/org.eclipse.rcptt.runner.runner-feature/feature.xml
```
Dependencies are not included. To work with indirect dependencies use `rdepends`.

## Rdepends
To find out which of your units depend on something, use `rdepends` (reverse dependencies):
```
$ rdepends org.eclipse.pde.core
feature:org.eclipse.rcptt.rap.ui.feature
product:org.eclipse.rcptt.runner.headless
....
plugin:org.eclipse.rcptt.launching.remote
plugin:org.eclipse.rcptt.launching.multiaut
plugin:org.eclipse.rcptt.launching.ext
plugin:org.eclipse.rcptt.ui
plugin:org.eclipse.rcptt.launching
```
The output is sorted by the length of indirect dependency chain.

## Why
`why <unitA> <unitB>` prints dependency chain between two units.

# TODO
Document other scripts
