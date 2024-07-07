restore-tabs
===

This is a tool for restoring tabs from crashed Chrome, which works on 64-bit Linux and was
tested on Chrome version 124.0.6367.78. If you have a coredump file of the main browser process
such as `core.chrome.1000`, use can run the tool as follows, and it will try to recover the multiset
of tabs that were open at the moment of the crash (including Incognito tabs, but the tab order
is not at all preserved):
```sh
python -m restore_tabs core.chrome.1000
```
