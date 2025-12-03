Goal:

Replace legacy URLs with updated static pages that guide users to new PROD URLs—without redirect logic in CloudFront or Akamai.

⸻

1. Pre-Cutover Validation (Akamai Team)

1.1 Akamai makes the new site public
	•	Confirm that the new downloads endpoints under Akamai are reachable externally.

1.2 Validate external access
	•	Test from:
	•	Internal network
	•	Personal home network
	•	Mobile device over LTE
	•	Ensure the new PROD URLs resolve and load correctly.

⸻

2. Update Static Pages in (S3 – West Bucket)

2.1 Take backup

Before making any changes:
	•	Download and store a copy of the existing index.html files for both:
	•	Save backups in a safe location for rollback.

2.2 Update new static pages
	•	Upload the updated static pages containing:
	•	The informational banner
	•	The message that SAC downloads have moved
	•	The new PROD URLs (LA and LW)
	•	Confirm correct file names and correct folder path structure.

⸻

3. CloudFront Update

3.1 Run a CloudFront invalidation

After uploading the updated static pages, invalidate:

/distribution/*

This forces CloudFront to fetch the new static pages from S3 instead of serving cached legacy content.

3.2 Wait for propagation
	•	Invalidations typically complete within a few minutes.
	•	Confirm status = Completed before testing.

⸻

4. Post-Cutover Testing

4.1 Clear browser cache

To avoid loading stale cached content from your browser.

4.2 Test the legacy URLs

For example:


4.3 Verify expected behavior

You should see:
	•	The newly updated static page
	•	Banner displaying updated messaging
	•	Clickable links to the new PROD URLs
	•	Clicking the links should successfully load the new PROD download pages hosted on Akamai

4.4 Validate across multiple locations

Check from:
	•	Internal workstation
	•	Home network
	•	Mobile device

⸻

5. Rollback Plan (If Needed)

If any issue occurs:
	•	Restore original index.html files from backup to the S3 bucket.
	•	Run CloudFront invalidation again:

/distribution/*

Re-test legacy URLs to confirm restoration.
