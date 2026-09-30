```
+-----------------------------+       +-----------------------------------+
|   Windows (Host OS)         |       |   WSL2 (e.g., Ubuntu)             |
|                             |       |                                   |
|  C:\Users\<you>\.ssh        | <---->|  /mnt/c/Users/<you>/.ssh          |
|   - id_rsa                  |       |    (same files, accessed via      |
|   - id_rsa.pub              |       |     Windows file system)          |
|   - config                  |       |                                   |
|                             |       |  /home/<you>/.ssh                 |
|   (central store)           |       |   - id_rsa (symlink to Windows)   |
|                             |       |   - id_rsa.pub                    |
|                             |       |   - config                        |
+-----------------------------+       +-----------------------------------+

    Arrow (←→)  =  /mnt/c mount point exposing Windows drive inside WSL2
    Arrow (↔)   =  symbolic-link from WSL2's home to the Windows .ssh folder
```