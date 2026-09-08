# Repository access and review distribution

## SSCR review access

The [SSCR submission guidelines](https://journals.sagepub.com/author-instructions/ssc) encourage sharing research data in a suitable public repository and linking to it in a data availability statement. They do not mandate GitHub. Their detailed peer-review policy and manuscript-file instructions require author anonymity, even though the page's short summary contains a conflicting review-model label. Check the detailed policy and submission-system instructions when providing reviewer access.

The submission-stage GitHub copy is intended for private author storage. A private repository URL is accessible only to authorized collaborators and cannot serve as an anonymous reviewer link. An ordinary public GitHub repository also exposes account ownership and commit metadata even if the files themselves omit author names.

For review, provide the archive through the journal's confidential supplementary-file channel if its file-size limits permit, or use a repository service that supports a tested anonymous read-only link. Verify the actual reviewer view before replacing `[ANONYMOUS REVIEW URL]` in submission documents. No working anonymous link is created or claimed by these files.

## File size and integrity

The main compressed CSV is approximately 62 MiB and is transported as eight lossless binary parts, each at most 8 MiB. The verifier reassembles and checks the original gzip. Keep all parts and the rest of the directory structure when downloading or copying the repository. GitHub permits ordinary Git files below 100 MiB, but the web upload form has a 25 MiB per-file limit. See [GitHub's large-file documentation](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

Before distribution, run:

```bash
python code/verify_package.py
```

The manifest describes the frozen released file state. Recomputing tables, notebooks or figures may change bytes because of numeric formatting, timing fields and image metadata. Compare results before deliberately updating a release manifest; do not rebuild it merely to conceal unexplained differences.

## Permanent archival release

After acceptance, update citation metadata with author names and article information, select a code/data license, and deposit the versioned release in a persistent repository if a DOI is needed. GitHub alone does not issue an archival DOI. The present anonymous citation metadata contains no invented article DOI or repository DOI.

Keep the manuscript, title page, cover letter, reviewer correspondence, local credentials and working-machine Git history outside the review archive.
