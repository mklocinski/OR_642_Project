INPUT_COLUMNS = {'Scraped': {
                    'Date':'date',
                    'Start Time':'time',
                    'End Time':'time',
                    'Authors':'string',
                    'Talk':'string',
                    'Working Group':'string',
                    'Classification':'string'
                },
                    'Abstract Data': {
                    'PresentationID': 'string',
                    'Status': 'string',
                    'PresentationTitle':'string',
                    'PresentationTrackDesc': 'string',
                    'PreferredTimeSlot': 'string',
                    'PreferenceLevel':'string',
                    'AuthorID':'string',
                    'Classification':'string',
                    'Distribution Statement':'string'
                },
                 'Schedule Data': {
                     'Day': 'date',
                     'Slot Begin Time':'time',
                     'Slot End Time':'time',
                     'Slot ID':'string',
                     'StartDayFlag':'string',
                     'EndDayFlag':'string'
                 },
                 'Preference Data': {
                     'Key': 'string',
                     'Description': 'string',
                     'Value': 'numeric'
                 }
                }

INPUT_FILE_PARSE = {'Abstract Data':'abstract-data',
                    'Schedule Data':'schedule-data',
                    'Preference Data':'preference-data'}


OUTPUT_COLUMNS = {'Presentation': 'string',
                  'Working Group': 'string',
                  'Authors': 'string',
                  'Date': 'date',
                  'Start Time': 'time',
                  'End Time': 'time',
                  'Duration': 'numeric'}
