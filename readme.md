# Update whitelist

Just a quick script to add whitelist entries across all desired networks. Run 
using python3.

In Dashboard, assign network tag "update_whitelist" to all networks that you 
want to add the whitelist entries to. You can do this from Organization > Overview.
Exapand the table, select desired networks (maybe test one first!) and add tag.

If not installed, install both requests & Meraki Dashboard API Python modules:
pip[3] install --upgrade requests
pip[3] install --upgrade meraki

This script iterates through the org's networks that are tagged with the label
"update_whitelist". For each of these networks'

When done, remove the network tag/label "update_whitelist" from Org > Overview.

#### Usage
python[3] update_whitelist.py -k <api_key> -o <org_id> -w <domains, comma-separated>

Example:
```
python3 update-whitelist.py -k 0123456789abcdefghi0123456789abcdefghi -o 591661234567890123 -w "meraki.com,cisco.com"
```




