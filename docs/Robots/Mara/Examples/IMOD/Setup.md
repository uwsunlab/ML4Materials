# How to set up Mara for IMOD data collection

## Step 1: Connect to UWSunLab wifi
Why? Mara is connected to the router called UWSunlab. This makes Mara's IP address the wifi router.

Wifi: UWSunLab
Password: ML4Science

## Step 2: Find Mara and your laptop's IP address
### Mara's IP
To operatre Mara, you need to find your computer's IP address and Mara's IP address so that you can send Mara csv files to read.

Mara's has two IP address, Wired and Wireless:
- Wired:  192.168.0.103
- Wireless: 192.168.0.104

Save this to set up Mara's kernel on VS Code

! Note ! Mara's IP can change if router restarts. Go to Mara's opentron app to check what the new IP is.

### Your Laptop's IP
To find your IP address, open a new terminal on VS code (Recommended) or you can use Window - powershell or Mac -Terminal app. 

If you have a Windows, type into terminal: 
```ipconfig``` then Look for  "IPv4 Address"

If you have a Mac, type into terminal:
```ipconfig getifaddr en0``` 

Save this IP adress somewhere since you will need to call it from Mara's server.

## Step 3: Setup Mara's Kernel on VS Code
To run Mara from VS code on your laptop, you need Mara's IP to be connected to the kernel
1. Open a new Jupyter Notebook (.ipynb)
2. Choose kernel from top right corner of the notebook







