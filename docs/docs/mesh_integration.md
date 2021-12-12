# MeshCentral Integration

## Overview

Gueen RMM integrates with [MeshCentral](https://github.com/Ylianst/MeshCentral) for the following 3 functions:

- Take Control
- Real time shell
- Real time file browser

At some point in the future, these functions will be directly built into the gueen Agent, removing the need for MeshCentral.

It should be noted that Gueen RMM and MeshCentral are 2 completely separate products and can run independently of each other.

They do not even have to run on the same box, however when you install Gueen RMM it simply installs meshcentral for you with some preconfigured settings to allow integration.

It is highly recommended to use the MeshCentral instance that gueen installs, since it allows the developers more control over it and to ensure things don't break.

## How does it work

MeshCentral has an embedding feature that allows integration into existing products.

See *Section 14 - Embedding MeshCentral* in the [MeshCentral User Guide](https://info.meshcentral.com/downloads/MeshCentral2/MeshCentral2UserGuide.pdf) for a detailed explanation of how this works.

The Gueen RMM Agent keeps track of your Mesh Agents, and periodically interacts with them to synchronize the mesh agent's unique ID with the Gueen RMM database.

When you do a take control / terminal / file browser on an agent using the gueen UI, behind the scenes, gueen generates a login token for meshcentral's website and then "wraps" MeshCentral's UI in an iframe for that specific agent only, using it's unique ID to know what agent to render in the iframe.
