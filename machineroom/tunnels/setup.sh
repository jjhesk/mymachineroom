#!/bin/bash

# Set the download URL and destination directory
url="https://github.com/Timac/VPNStatus/releases/download/3.0/vpnutil.zip"
dest_dir="/Users/hesdx/go/bin"
proxy="http://127.0.0.1:7890"
# Create the destination directory if it doesn't exist
mkdir -p "$dest_dir"
# Download the file to the destination directory
curl -x $proxy -o "$dest_dir/_p.zip" "$url"
# Extract the contents of the zip file to the destination directory
unzip -d "$dest_dir" "$dest_dir/_p.zip"
