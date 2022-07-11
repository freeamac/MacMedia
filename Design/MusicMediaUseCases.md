# Music Media Use Cases

## Search collection for an Album
---

### **Main Success Scenario:**

1. User invokes system
2. System displays main display
3. System displays list of Albums in collection
4. User invokes search function
5. System displays search function
6. User specifies search criteria
7. User invokes search
8. System displays Albums matching search criteria
9. User selects Album from list to display details
10. System displays information about selected Album

### **Extensions:**

  3A. No Albums exist:
  1. User can add new Album
  2. Return to MSS 2

  5A. User selects Album(s) from collection list to display:
  1. Return in MSS 10

  7A. User cancels search:
  1. Return to MSS 3

  8A. System finds no Albums matching search criteria:
  1. System displays message that no item found
  2. User acknowledges message
  3. Return to MSS 3

  ---
  ## Add Album to collection
  ---

  ### **Main Success Scenario:**

  1. User invokes system
  2. System displays main display
  3. System displays list of Albums in collection
  4. User involes add Album function
  5. System displays add new Album function
  6. User specifies new Album information
  7. User invokes save new Album information
  8. System validates new Album information
  9. System adds new Album information to the collection
  10. System displays new Album information

  ### **Extensions:**

  3A. No Albums exists:
  1. User can still add new Album, MSS 4

  7A. User cancels add Album information:
  1. Return to MSS 3

  8A. Album already exists in collection:
  1. Return to MSS 6 with already entered information

  ---
  ## Delete Album from collection
  ---

  ### **Main Success Scenario:**

  1. Complete "Search collection for an Album"
  2. User selects Album to delete from search result
  3. User invokes delete Album function
  4. System asks for confirmation of deletion
  5. User confirms delete
  6. System deletes Album from collection
  7. System displays update list of Albums in collection, MSS 3 in "Search collection for an Album"

  ### **Extensions:**

  4A. User cancels deletion
  1. Return to MSS 1

  ---
  ## Modify Album information
  ---

  ### **Main Succes Criteria:**

  1. Complete "Search collection for an Album"
  2. User selects Album to modify from search result
  3. User invokes modify Album function
  4. System display modify Album function 
  5. User updates Album information
  6. User invokes save modified information function
  7. System validates modified Album information
  8. System update Album information with modifications
  9. System displayed modified Album information

  ### **Extensions:**

  4A. User cancels modify Album function
  1. Return to MSS 1

  6A. User cancels modify Album function
  1. Return to MSS 1

  7A. Modified information conflicts with another Album in collection
  1. System notifies user of conflict
  2. Return to MSS 4