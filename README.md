# Risk Manager
- **Authors**:		Simon Balz <simon@balz.me>, Mika Borner <mika.borner@gmail.com>, Christoph Dittmann <mulibu.flyingk@googlemail.com>, Harun Kuessner <h.huessner@posteo.de>
- **Description**:	Risk Manager
- **Version**: 		1.0.1

## Introduction
The Risk Manager adds risk scoring functionality to Splunk.

## Features

-Assigns risk scores to risk objects (e.g. users, hosts etc.)
-Track security and/or operational risks
-Collect and store contributing data that caused risk scores to increase/decrease
-Analyze and Report Risk Events
-Encrypt risk metadata and contributing data (Workplace Privacy)
-Pivot over risks

## Additional Notes for Apptitude App Contest

-Risk Manager is part of the Hyperthreat-Suite

## Release Notes
- **v1.0.1**	/	2015-07-26
	- Minor improvement for risk_settings	

- **v1.0**	/	2015-07-20
	- First major release for Apptitude2 submission

- **v0.1**	/	2015-06-14
	- First check in

## Changelog
- **2015-07-19** mika.borner@gmail.com
	- First Release

## Credits
Libraries and snippets:
- Handsontable (http://handsontable.com/)

## Prerequisites
- Splunk v6.2+ (we use the App Key Value Store)
- Alerts (Saved searches with alert actions)
- Technology Add-on for Risk Manager
- If encryption is used, (Support Add-on for SA-hypercrypt)

## Documentation
- Homepage: https://github.com/my2ndhead/risk_manager
- Wiki: https://github.com/my2ndhead/risk_manager/wiki

## License
- **This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.** [1]
- **Commercial Use, Excerpt from CC BY-NC-SA 4.0:**
  - "A commercial use is one primarily intended for commercial advantage or monetary compensation."
- **In case of Risk Manager this translates to:**
  - You may use Risk Manager in commercial environments for handling in-house Splunk alerts
  - You may use Risk Manager as part of your consulting or integration work, if you're considered to be working on behalf of your customer. The customer will be the licensee of Risk Manager and must comply according to the license terms
  - You are not allowed to sell Risk Manager as a standalone product or within an application bundle
  - If you want to use Risk Manager outside of these license terms, please contact us and we will find a solution

## References
[1] http://creativecommons.org/licenses/by-nc-sa/4.0/
