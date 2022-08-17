# SB2WAV
Bulk converts SMPC soundbank files to .wav &amp; .wav to .wem

![pre](https://i.postimg.cc/6583nRnY/pre.gif)

# Notice
Due to how the [pyinstaller](https://github.com/pyinstaller/pyinstaller) bootloader works, Windows Defender might detect the release as a virus. Read more: https://github.com/pyinstaller/pyinstaller/issues/6062

Alternatively you can compile yourself
```
pip install pyinstaller
pyinstaller -F -w -n "SB2WAV" main.py
```

