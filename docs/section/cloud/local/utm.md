# Tutorial 2: Using UTM

UTM is a powerful, native macOS application that uses Apple's Hypervisor virtualization to run operating systems (including Linux distributions) with a graphical interface or in headless mode.

## Step 1: Install UTM

You can download UTM for free from the official website or install it via Homebrew Cask:

```bash
brew install --cask utm

```

## Step 2: Create a Linux Virtual Machine

1. Open **UTM** from your Applications folder.
2. Click **Create a New Virtual Machine**.
3. Select **Virtualize** (since you are running ARM64 Linux on Apple Silicon, or x86_64 on older Intel Macs).
4. Choose **Linux** as the operating system.
5. Download and select an ARM64 (or x86_64) Ubuntu Server or Debian ISO image.
6. Allocate your desired memory (e.g., 4 GB or more) and storage space, then finish the setup wizard.

## Step 3: Start and Access the Virtual Machine

1. Click the **Play** button on your newly created Ubuntu VM in the UTM sidebar.
2. Follow the standard on-screen prompts to complete the Ubuntu installation.
3. Open a terminal inside the Ubuntu guest OS (or SSH into it from your Mac terminal).