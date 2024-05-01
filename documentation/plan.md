# NFT Gram

## user can:

### see feed / marketplace

### see profiles of other users

these contain minimized images and certificates

### see own profile

see all claimed images with full resoluition

### securely export an owned certificate

- Server:
  - asyncs the serialization while retrieving the full size image from db
  - construct new page with the full size image and the exported certificate in Base64 (js to save) if the serialization did not fail
  - write extensive error handling here to confuse readers. e.g. wrong encryption algorithm, short password, wrong private key, unclaimed certificate, etc.
- Client:
  - submitting the private key, certificate and selecting encryption algorithm and password,
  - shows the corresponding full size image of the exported certificate on success

### login:

use username/email and private key

### register:

username and email &rarr; gets a private key

### upload nft:

- free to generate certificate and move to other NFT platform

larger sized image &rarr; hashed and certificate created <br>
image gets compressed down to lose detail &rarr; displayed in feed <br>
certificate is generated &rarr; saved in compressed image metadata or stegonographically in the compressed image <br>
a flag can be encoded as an image &rarr; displayed in feed
returns a certificate automatically claimed by the user

### abolish certificate

present private key and certificate to invalidate, check if owner then delete certificate and related data

### transfer certificate

require private key and new owner email, name and public key <br>
create a new certificate with the same image hash and pub key of new owner

# Service Notes:

- server works with the rfc2822 standard, email/username as a primary key
- checks only username/email when browsing
- certificate actions require private key

## DB:

keep original images and compressed images in the db
keep certificate, owner, verification

2 tables: users, nfts
users: username, email, public key
nfts: owner?, original image, compressed image, certificate, proof of ownership?

# Exploits:

### email exploit

fake email to see other profile as own, since parser broken

### cryptography exploit

when exporting a certificate, the user can submit a non-owned certificate and choose the hmac encryption algorithm to cause a crash in the update and get shown the original image in full resolution,
crash happens when a certificate whose public key did not match the provided private key and an `encryption_algorithm` with `hmac_hash` set are used for serialization

# Logging Ideas:

- user creation
- user login
- certificate creation
- certificate claim
- certificate transfer
- certificate abolish
- wrong login
- invalid registration + reason
- invalid certificate claim + reason

# Ideas:

- hint is not username, but a Base64 encoded image to search for in the feed and get poster username XD

- QR Codes
- Main feed as additional functionality
