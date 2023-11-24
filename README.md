# IntegriMark Action

This GitHub Action automates the process of encrypting PDF files using IntegriMark and publishing them to GitHub Pages. It's designed to enhance the security and traceability of digital PDF documents by watermarking them with unique, user-specific details.

**CURRENTLY UNDER BETA-TESTING, PLEASE SEND FEEDBACK AND EXPECT BUG!**

## Features

- **Automated Encryption**: Securely encrypts PDF files and stores them in a `_bundle` directory.
- **Unique Password Generation**: Each file is encrypted with a unique, automatically generated password.
- **Customized URL Generation**: Creates customized URLs for each encrypted file, tailored for controlled distribution.
- **Easy Hosting on GitHub Pages**: Automatically publishes the encrypted files to a specified GitHub Pages branch.

## Usage

To use this action in your workflow, add the following step to your `.github/workflows` YAML file:

```yaml
- uses: jlumbroso/integrimark-action@v1
  with:
    base_url: 'https://your-custom-base-url.com' # Replace with your desired base URL
    files: '**/*.pdf' # Pattern to match files to process
```

### Inputs

- `base_url`: **Required** The base URL where the IntegriMark vault will be hosted.
- `files`: The glob pattern to match PDF files to be processed. Defaults to '**/*.pdf'.

### Example Workflow

Here's a complete workflow example:

```yaml
name: Encrypt and Publish PDFs

on:
  push:
    branches:
      - main

jobs:
  encrypt-and-publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - uses: jlumbroso/integrimark-action@v1
      with:
        base_url: 'https://your-custom-base-url.com'
        files: 'docs/**/*.pdf'
```

This workflow triggers on a push to the `main` branch, checks out the code, and then runs the IntegriMark action to process PDF files located in the `docs` directory.

## Additional Information

- Ensure that your repository has a `gh-pages` branch for GitHub Pages deployment.
- The action will commit the `passwords.json` file to the main branch and the encrypted PDF files to the `gh-pages` branch.

## Contributing

Contributions to the IntegriMark Action are welcome! Please submit a pull request with your changes.

## License

This GitHub Action is released under the [LGPLv3 License](LICENSE.md).

## Acknowledgments

This action was created by [Jérémie Lumbroso](https://github.com/jlumbroso). For more information about IntegriMark, visit the [IntegriMark repository](https://github.com/jlumbroso/integrimark).