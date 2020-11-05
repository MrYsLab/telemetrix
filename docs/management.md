# Cleanly Shutting Down

## shutdown
You should always call the shutdown method to cleanly exit your application and to assure
that any streaming data coming from the Arduino-core device is halted.

```python
 def shutdown(self)

    This method attempts an orderly shutdown.
    If any exceptions are thrown, they are ignored.
```
**Examples:**

All the examples call shutdown.

<br>
<br>

Copyright (C) 2020 Alan Yorinks. All Rights Reserved.
