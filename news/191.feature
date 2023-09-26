Add ``dos_protection`` config.
With Zope 5.8.4+ you may get `zExceptions.BadRequest: data exceeds memory limit`` when uploading an image or file of more than 1 MB.
To increase this limit, you can add this in your instance recipe, and choose your own limit:
```
zope-conf-additional =
  <dos_protection>
    form-memory-limit 4MB
  </dos_protection>
```
[@mamico]
