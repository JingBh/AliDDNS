# AliDDNS
Use Aliyun DNS as a DDNS service.

## How to install

### Clone the project
```bash
git clone https://github.com/JingBh/AliDDNS.git
cd AliDDNS
pip install -r requirements.txt
```

### Copy the config
```bash
cp config.example.ini config.ini
# edit config.ini
```

### What's in `config.ini`

#### `[auth]`
Just put in your Aliyun AccessKeyId and AccessKeySecret.

#### `[main]`

##### `frequency` *integer*
 - **0** : Only run once.
 - **Any number bigger than 0** : Run every that much seconds.

##### `domain` *string*

##### `ipv4` *boolean*

##### `ipv6` *boolean*
