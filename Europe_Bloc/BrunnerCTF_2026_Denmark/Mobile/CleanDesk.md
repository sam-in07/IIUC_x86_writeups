  ### Walkthrough & Solution
  #### 1. Unpacking the Android Backup (.ab)
  The file cleandesk.ab is an unencrypted Android Backup archive. By stripping the 24-byte header (ANDROID BACKUP\n5\n1\nnone\n) and decompressing the remaining zlib
  stream, we obtain a standard tar archive containing the application data for dk.brunnerne.onevoice.

  Extracted structure:

  • sp/keystore_backup.xml
  • sp/dk.brunnerne.onevoice_preferences.xml
  • sp/session.xml
  • db/notes.db
  • db/statements.db
  • f/statement-archive.seal
  • f/offboarding-checklist.txt
  ──────
  #### 2. Locating the Encryption Key

  In sp/keystore_backup.xml, the app backed up its content encryption key into SharedPreferences:
    <map>
        <string name="content_key">6mqMbv76RDT1G7yib5XrsS5DolJ+pPfZAGacZN3cTsc=</string>
        <string name="content_key_alg">AES-256-GCM</string>
        <string name="sealed_layout">nonce[12] || ciphertext || tag[16]</string>
        <string name="sealed_aad">none</string>
        <int name="content_key_version" value="3" />
        <boolean name="device_bound" value="true" />
    </map>
  ──────
  #### 3. Decrypting the Database Records

  The database notes.db contains encrypted Base64-encoded messages in the messages table. Decrypting them using AES-256-GCM (nonce[12] || ciphertext || tag[16]) reveals
  the chat history:

  • Msg 9 (Mette Holm): One more thing before you go. The offboarding checklist says IT images the handset before the wipe. Ask them where the image goes.
  • Msg 10 (Hanne Bak): Already did. It goes on the shared drive, with everything on it. brunner{4llowB4ckup_t00k_th3_k3y_t00}
  • Msg 11 (Mette Holm): Of course it does.
  ──────
  ### Flag

    brunner{4llowB4ckup_t00k_th3_k3y_t00}