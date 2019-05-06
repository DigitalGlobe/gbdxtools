## RDA Template Creation Guide

### Getting Started

- Requirements:
  - GBDX credentials
  - Postman, Python requests library, etc
  - Web browser
  
- RDA Template API documentation
  - https://rda.geobigdata.io/docs/api.html#/  
  - https://rda.geobigdata.io/docs/
  
- RDA tools is helpful with template creation as well
  - https://github.com/DigitalGlobe/rdatools#rda-template  

### Creating a RDA Template

- Using a web browser navigate to https://graphstudio.geobigdata.io/

- Login using GBDX credentials

- Select `Template` Tab at top center of page
  - Once Template tab has been selected you can start adding operators to the template.
  - Drag operators to the graph pane and supply arguments
    - Arguments can be hardcoded or passed in via URL query params
    - To pass in arguments, simply use `${yourArgName}` in leu of a hardcoded string.
    - To have a default argument (e.g. `WGS84`), simply use `${yourArgName:-WGS84}`
      - Note `:-` is the seperator between argument and default value.
  - Connect the nodes (operators) using edges
  - Edge selection is documented in the operator descriptions
  - Lastly select a default Node Id
  
- Once you're template is created you can pass in arguments and view the results in the right window pane.

- To publish template simply click `save graph` and store the template id

### Creating RDA Template Metadata

- You can create template metadata to make your template searchable.
- You can also reference your template by name if metadata is created
  - **GBDXtools requires templates to be referenced by name**

- Sample template metadata

```
{
    "isPublic": false,
    "keywords": [
        "<your_searchable_name>"
    ],
    "sensors": [
        "<sensor>"
    ],
    "keynodes": [
        {
            "id": "<operator_name>",
            "description": "<description>"
        }
    ],
    "description": "<description>",
    "metadataAuthor": {
        "firstName": "<name>",
        "familyName": "<name>",
        "email": "<email>"
    },
    "templateAuthor": {
        "firstName": "<name>",
        "familyName": "<name>",
        "email": "<email>"
    },
    "name": "<your_searchable_name>",
    "templateId": "<your_template_id>",
}
```

- Using Postman:

  - Update the above sample template metadata
  - `POST` template metadata to `https://rda.geobigdata.io/v1/template/metadata`
  - Capture metadata Id for late updating. If the metadata id is lost, one can query the metadata by searching.
    - https://rda.geobigdata.io/v1/template/metadata/search?free-text=`YourTemplateName`
    
### Searching for RDA template metadata

- A user can search for template metadata using a valid template name

- Example:
  - https://rda.geobigdata.io/v1/template/metadata/search?free-text=IdahoTemplate    
  
  



