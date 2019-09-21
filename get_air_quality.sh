#!/bin/bash 

# ADD TO CRONTAB using "cron -e" then: 5 * * * * (/home/pi/Development/get_air_quality.sh 2>&1) >/dev/null 2>&1

# --------------------- AIR QUALITY INDEX (0-100) ----------

polution=`curl -sL "http://www.air-rhonealpes.fr/monair/commune/69385"  | awk "/class=\"indice\"/ {print $1}" | grep class=\"indice\"\> |sed 's/^.*<div.*">\(.\{1,3\}\)<\/div>/\1/g' `

# Sending to DOMOTICZ
echo Sending Air Quality Index to Domoticz Server...
domo_url='http://192.168.1.30:8084/json.htm?type=command&param=udevice&idx=23&nvalue=0&svalue='$polution
echo $domo_url
curl $domo_url
echo Done.

# --------------------- ATMO ALERT & INDEX (1-9)  ----------

# Get Atmo Alert & Index
atmo=`curl -sL http://www.air-rhonealpes.fr/indice/atmo | awk "/pollutant|Lyon/ {print $1}" | grep -A 1 Lyon | grep pollutant | sed 's/^.*>\(.*\) | \(.*\)<\/span>/\1. \2/g'`

# Keep only Index
atmo_idx=`echo $atmo | sed 's/\..*//'`

# Escaping [SPACE] in ATMO Alert Label
atmo=`echo $atmo | sed 's/ /%20/g'`

# Converting ATMO Index (1-10) to Alert Level (0-5)
atmo_alert=$((atmo_idx / 2))

# Sending Alert Level to DOMOTICZ
echo Sending ATMO Index to Domoticz Server...
domo_url="http://192.168.1.30:8084/json.htm?type=command&param=udevice&idx=24&nvalue=${atmo_alert}&svalue=${atmo}"
echo $domo_url
curl $domo_url

# Sending Alert Index to DOMOTICZ for graphic chart
domo_url="http://192.168.1.30:8084/json.htm?type=command&param=udevice&idx=25&nvalue=0&svalue=${atmo_idx}.000"
echo $domo_url
curl $domo_url
echo Done.

# -------------------- BITCOIN VALUE -------------
#
# Get BitCoin / OkCash  current price
# 
#ok=`curl -s https://www.litebit.eu/en/buy/okcash`
ok=`curl -s https://api.coinmarketcap.com/v1/ticker/okcash/?convert=EUR`
#ok=`echo $ok | sed -r 's/.*coin-v[a-z]+"\s+value="([0-9\.]+)".*/\1/' `
ok=`echo $ok | sed -r 's/.*price_eur":\s"([0-9\.]+)".*/\1/' `
echo "OKCash value: " $ok    

# Sending to DOMOTICZ
echo Sending OKCASH Value to Domoticz Server...
domo_url='http://192.168.1.30:8084/json.htm?type=command&param=udevice&idx=36&nvalue=0&svalue='$ok
echo $domo_url
curl $domo_url
echo Done.

# ---------------------- POLLEN ALERT -------------

# Getting POLLENs from www.air-rhonealpes.fr for LYON

# Reading Air Quality Pollens
pollens=`curl -sL http://www.air-rhonealpes.fr/allergie-pollen/indice-pollinique | \
                                                           sed 's/\\u003./\n/g' | \
                                                           sed 's/\\u00e9/e/g'  | \
                                                           sed 's/\\u00e8/e/g'  | \
                                                           grep -A 4 'Lyon'  `
echo "pollens1: " $pollens
pollens=`echo $pollens | tr -d '\\\\'`
echo "pollens2: [" $pollens "]"
#pollens=`echo $pollens | awk 'BEGIN {r["Nul"]=0;r["Tr  s faible"]=1;r["Faible"]=2;r["Moyen"]=3;r["Elevu00e9"]=4;r["Tr  s   lev  "]=5}  /Lyon/{v=$3;print v,r[$8],$8 }' `
#pollens=`echo $pollens | awk -F ' : ' 'BEGIN {r["Nul"]=0;r["Tres faible"]=1;r["Faible"]=2;r["Moyen"]=3;r["Eleve"]=4;r["Tres eleve"]=5} /Risque/{print r[$3] }' `
pollens=`echo $pollens | awk -F '[:-]+' 'BEGIN {r["Nul"]=0;r["Tresfaible"]=1;r["Faible"]=2;r["Moyen"]=3;r["Eleve"]=4;r["Treseleve"]=5} /Risque/{gsub(" ","",$3);print r[$3]}' `
echo "pollens3: [" $pollens "]"
echo Air Quality Pollens: $pollens

pollens_idx=`echo $pollens | cut -d ' ' -f 2`

# Sending to DOMOTICZ
echo Sending Air Quality Pollens to Domoticz Server...
domo_url='http://192.168.1.30:8084/json.htm?type=command&param=udevice&idx=26&nvalue=0&svalue='$pollens_idx
echo $domo_url
curl $domo_url

# ----- RADIATION in LYON -----
/usr/bin/python /home/pi/Development/test_basic.py
pkill chrom  #Kill the remaining {chromium} and  {chrome-driver} processes after python program is completed

