"""
#!/bin/bash

# Set the download URL and destination directory
url="https://github.com/Timac/VPNStatus/releases/download/3.0/vpnutil.zip"
dest_dir="/Users/hesdx/go/bin"

# Create the destination directory if it doesn't exist
mkdir -p "${dest_dir}"

# Download the file to the destination directory
curl -o "${dest_dir}/vpnutil.zip" "${url}"

# Extract the contents of the zip file to the destination directory
unzip -d "${dest_dir}" "${dest_dir}/vpnutil.zip"
"""


