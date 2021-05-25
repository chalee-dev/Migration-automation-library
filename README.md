# AWS Migration Automation Library
AWS Migration Automation Library is an collection of tools and automation scripts to automate and acclerate AWS migrations, we encourage everyone in AWS to contribute and share.

## Contributing to this library
* If your automation is related to the CloudEndure Migration Factory solution, please create a subfolder inside    CloudEndure Migration Factory for your automation scripts or tools.
* If you are going to build a new Migration automation solution, please create a folder at the same level as CloudEndure Migration Factory solution
* Please update your code with the following file structure, and use the README file as the instruction for your automation scripts or tools
* Use the Update DNS dynamic registration on Windows automation as your example if needed

## File Structure

```

|-Your Solution Name/Your Automation Name/
  |-yourcode             [ Your code for the automation, can be Python script or anything related to the solution ]
  |-README.md            [ Instructions for user to use your automation ]

Example:
|-CloudEndure Migration Factory/Update DNS dynamic registration on Windows/
  |-CEMF-Update-Windows-DynamicDNS.py   
  |-README.md

```
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the the MIT-0 License. See the LICENSE file.
This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions and limitations under the License.
