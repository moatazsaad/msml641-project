# Production and demo runbook

## Stable demo schedules

- Primary: `CMSC330, CMSC351, STAT400`
- Backup: `CMSC216, CMSC250, MATH141`

These courses are included in the committed DistilBERT profile cache so a
fresh session does not need PlanetTerp access or first-time model inference.

## Pre-demo checks

1. Clone the exact release commit and run `git lfs pull`.
2. Confirm `results/distilbert_model/model.safetensors` is about 268 MB, not a
   short text pointer.
3. Run `python src/test_course_profile_service.py` and the other
   `src/test_*.py` modules.
4. Start with `streamlit run app.py`, open a private browser window, and test
   both schedules above.
5. Test one uncached valid course and temporarily disable networking to verify
   the error state.
6. Capture screenshots and a short screen recording of the primary schedule;
   store them outside the repository or add them under `docs/demo_assets/`.

## Hosting requirements

- The host must install Git LFS and materialize the model artifact during its
  build. Startup now fails with an actionable error if only the pointer exists.
- The committed profile cache makes demo courses independent of writable
  runtime storage. Newly inferred profiles persist only when the host provides
  a durable writable filesystem; ephemeral Streamlit hosts reset them on a
  rebuild/restart.
- Validate the public URL from a signed-out/private browser before presenting.
