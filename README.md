LATENCY_ELIMINATOR - SETUP & RUN INSTRUCTIONS
==============================================

You now have 5 Python files. Copy them to your LATENCY_ELIMINATOR folder:

📁 Your folder structure should be:
```
LATENCY_ELIMINATOR/
├── .env                          (already created)
├── venv/                         (already created)
├── api_client.py                 (NEW - copy this)
├── script_executor.py            (NEW - copy this)
├── memory_simple.py              (NEW - copy this)
├── memory_redis.py               (NEW - copy this)
├── agent.py                      (NEW - copy this)
└── test_script.py                (NEW - copy this)
```

STEP 1: Copy all 5 .py files to your LATENCY_ELIMINATOR folder

STEP 2: Open Command Prompt/PowerShell in your LATENCY_ELIMINATOR folder

STEP 3: Activate virtual environment:
```
venv\Scripts\activate
```

STEP 4: Install pandas (needed for test script):
```
pip install pandas
```

STEP 5: RUN THE AGENT:
```
python agent.py test_script.py
```

STEP 6: Follow the prompts:
- Agent will run the broken script
- Show the error
- Ask Claude to fix it
- Show you the proposed fix
- Ask for approval (type 'a' to approve)
- Store the fix for future reference

WHAT TO EXPECT:
✓ Script runs and detects the KeyError
✓ Claude proposes a fix
✓ You approve
✓ Fix is applied
✓ Script runs successfully
✓ Fix is stored in reference_fixes.json

TESTING WITH YOUR OWN SCRIPTS:
Simply create a broken Python script and run:
```
python agent.py your_broken_script.py
```

REDIS VERSION (Optional - skip for now):
If you want to test with Redis (production version):
```
python agent.py test_script.py --redis
```
(Requires Redis running separately)

Questions? Let me know!
