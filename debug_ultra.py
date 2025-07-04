#!/usr/bin/env python3
"""ULTRA DEBUG SCRIPT - Inject maximum logging into parse_response method."""

import re
import sys

# Read the current streams.py file
with open("/home/marlonsc/flext/flext-tap-oracle-wms/src/tap_oracle_wms/streams.py", encoding="utf-8") as f:
    content = f.read()

# Find the parse_response method and inject ULTRA logging
new_parse_response = '''    def parse_response(self, response: requests.Response) -> Iterable[dict[str, Any]]:
        """🔥 ULTRA-DEBUG: Parse records from API response with MAXIMUM visibility.

        Oracle WMS returns data in format:
        {
            "results": [...],
            "next_page": "...",
            "page_nbr": 1
        }
        """
        # 💥 FORCE DEBUG: Use error level for maximum visibility
        print(f"💥 PARSE_RESPONSE START - Entity: {self._entity_name}")
        self.logger.error(f"💥 PARSE_RESPONSE START - Entity: {self._entity_name}")
        self.logger.error(f"🌐 RESPONSE STATUS: {response.status_code}")
        self.logger.error(f"📏 RESPONSE SIZE: {len(response.content)} bytes")

        # Show first 1000 chars of raw response
        raw_text = response.text[:1000]
        print(f"📄 RAW RESPONSE (first 1000 chars): {raw_text}...")
        self.logger.error(f"📄 RAW RESPONSE (first 1000 chars): {raw_text}...")

        try:
            data = response.json()
            print(f"✅ JSON PARSE SUCCESS - Type: {type(data)}")
            self.logger.error(f"✅ JSON PARSE SUCCESS - Type: {type(data)}")

            # 🔍 ULTRA-DEBUG: Complete data structure
            if isinstance(data, dict):
                print(f"📂 DICT KEYS: {list(data.keys())}")
                self.logger.error(f"📂 DICT KEYS: {list(data.keys())}")

                if "results" in data:
                    results = data["results"]
                    print(f"📊 RESULTS TYPE: {type(results)}")
                    self.logger.error(f"📊 RESULTS TYPE: {type(results)}")

                    if isinstance(results, list):
                        print(f"📈 RESULTS COUNT: {len(results)}")
                        self.logger.error(f"📈 RESULTS COUNT: {len(results)}")

                        # Log first record as sample
                        if results:
                            first_record = results[0]
                            print(f"🎯 FIRST RECORD KEYS: {list(first_record.keys()) if isinstance(first_record, dict) else 'NOT_DICT'}")
                            self.logger.error(f"🎯 FIRST RECORD KEYS: {list(first_record.keys()) if isinstance(first_record, dict) else 'NOT_DICT'}")
                            print(f"🎯 FIRST RECORD SAMPLE: {str(first_record)[:200]}...")
                            self.logger.error(f"🎯 FIRST RECORD SAMPLE: {str(first_record)[:200]}...")
                    else:
                        print(f"❌ RESULTS NOT LIST: {results}")
                        self.logger.error(f"❌ RESULTS NOT LIST: {results}")

                if "next_page" in data:
                    print(f"➡️ NEXT PAGE: {data['next_page']}")
                    self.logger.error(f"➡️ NEXT PAGE: {data['next_page']}")

            elif isinstance(data, list):
                print(f"📝 DIRECT LIST - COUNT: {len(data)}")
                self.logger.error(f"📝 DIRECT LIST - COUNT: {len(data)}")
            else:
                print(f"❓ UNEXPECTED TYPE: {type(data)} - VALUE: {str(data)[:200]}")
                self.logger.error(f"❓ UNEXPECTED TYPE: {type(data)} - VALUE: {str(data)[:200]}")

            self._log_response_structure(data)

            # Extract records from results array
            if isinstance(data, dict) and "results" in data:
                print(f"🎉 YIELDING FROM RESULTS ARRAY")
                self.logger.error(f"🎉 YIELDING FROM RESULTS ARRAY")

                record_count = 0
                for record in self._yield_results_array(data):
                    record_count += 1
                    print(f"🎯 YIELDING RECORD #{record_count} - Keys: {list(record.keys()) if isinstance(record, dict) else 'NOT_DICT'}")
                    self.logger.error(f"🎯 YIELDING RECORD #{record_count} - Keys: {list(record.keys()) if isinstance(record, dict) else 'NOT_DICT'}")
                    yield record

                print(f"🏁 FINISHED YIELDING - TOTAL: {record_count} records")
                self.logger.error(f"🏁 FINISHED YIELDING - TOTAL: {record_count} records")

            elif isinstance(data, list):
                print(f"🎉 YIELDING FROM DIRECT ARRAY")
                self.logger.error(f"🎉 YIELDING FROM DIRECT ARRAY")

                record_count = 0
                for record in self._yield_direct_array(data):
                    record_count += 1
                    print(f"🎯 YIELDING RECORD #{record_count}")
                    self.logger.error(f"🎯 YIELDING RECORD #{record_count}")
                    yield record

                print(f"🏁 FINISHED YIELDING - TOTAL: {record_count} records")
                self.logger.error(f"🏁 FINISHED YIELDING - TOTAL: {record_count} records")
            else:
                print(f"❌ NO VALID FORMAT - Cannot extract records")
                self.logger.error(f"❌ NO VALID FORMAT - Cannot extract records")
                self._log_unexpected_format(data)

        except json.JSONDecodeError as e:
            # JSON decode errors indicate serious API issues
            print(f"💥 JSON DECODE ERROR: {e}")
            self.logger.error(f"💥 JSON DECODE ERROR: {e}")
            print(f"📄 RAW CONTENT (first 500 chars): {response.text[:500]}")
            self.logger.error(f"📄 RAW CONTENT (first 500 chars): {response.text[:500]}")

            self.logger.error(
                "Critical JSON parsing error for entity %s: Invalid response format. "
                "This indicates API incompatibility or server-side issues.",
                self._entity_name
            )
            msg = f"Invalid JSON response from WMS API for entity {self._entity_name}: {e}"
            # This is likely a retriable error (server issue)
            raise RetriableAPIError(msg) from e'''

# Replace the existing parse_response method
pattern = r"def parse_response\(self, response: requests\.Response\) -> Iterable\[dict\[str, Any\]\]:.*?except json\.JSONDecodeError as e:.*?raise RetriableAPIError\(msg\) from e"
new_content = re.sub(pattern, new_parse_response, content, flags=re.DOTALL)

# Write the modified content back
with open("/home/marlonsc/flext/flext-tap-oracle-wms/src/tap_oracle_wms/streams.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("✅ ULTRA DEBUG INJECTED - parse_response method now has maximum logging")
