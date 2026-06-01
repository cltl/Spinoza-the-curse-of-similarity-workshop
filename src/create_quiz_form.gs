/**
 * Whiteboard Quiz – Google Apps Script
 *
 * HOW TO USE:
 *  1. Go to https://script.google.com
 *  2. Click "New project", delete placeholder code, paste this file
 *  3. Save (Cmd/Ctrl+S)
 *  4. Click Run ▶  (function: createQuizForm)
 *  5. Accept permissions popup
 *  6. Check the Execution log at the bottom for the form and sheet URLs
 *
 * FORM FLOW FOR PARTICIPANTS:
 *  Page 1  : Enter team name
 *  Page 2  : Whiteboard 1 — 3 questions — click Next
 *  Page 3  : Whiteboard 2 — 3 questions — click Next
 *  ...
 *  Page 25 : Whiteboard 24 — 3 questions — click Submit
 *
 *  All answers for one team land in a single row in the linked Google Sheet.
 */

var QUIZ_DATA = [
  { n:  1, q3: "What HI use-case is discussed?" },
  { n:  7, q3: "What does a score of 1.2 mean?" },
  { n:  8, q3: "What do 0 and the text boxes represent?" },
  { n: 10, q3: "What does DPA stand for?" },
  { n: 11, q3: "What level was being detected?" },
  { n: 12, q3: "What does the straight line represent in the power-law-graph?" },
  { n: 15, q3: "What do WTL and NTL stand for?" },
  { n: 17, q3: "Is what Karla speaks a subject or complement gap?" },
  { n: 18, q3: "Which word is misspelled here?" },
  { n: 21, q3: "What is being placed in time?" },
  { n: 24, q3: "What is the green jigsaw puzzle suggesting?" }
];

function createQuizForm() {

  // Regular form (not quiz mode) so no email is required or collected
  var form = FormApp.create("Whiteboard Quiz");
  form.setDescription(
    "Answer 3 questions per whiteboard. Use Next to move to the next whiteboard.\n" +
    "Submit at the end after completing all 24 whiteboards.\n\n" +
    "Points per whiteboard (6 total):\n" +
    "  • Name of project / PhD / course / demo — 1 point\n" +
    "  • Month and year — 2 points\n" +
    "  • Special question — 3 points\n\n" +
    "Maximum total: 66 points"
  );
  form.setCollectEmail(false);
  form.setAllowResponseEdits(false);
  form.setLimitOneResponsePerUser(false);

  // ── Page 1: Team name ──────────────────────────────────────────────────────
  var teamItem = form.addTextItem();
  teamItem.setTitle("Team name");
  teamItem.setRequired(true);

  // ── Pages 2–25: one page per whiteboard ───────────────────────────────────
  for (var i = 0; i < QUIZ_DATA.length; i++) {
    var wb = QUIZ_DATA[i];

    // Page break — no setGoToPage call, so it defaults to CONTINUE (sequential)
    form.addPageBreakItem().setTitle("Whiteboard " + wb.n);

    // Q1 — name of project / PhD / course / demo  (1 point)
    var q1 = form.addTextItem();
    q1.setTitle("What is the name of the project, PhD, course, or demo?  (1 point)");
    q1.setRequired(true);

    // Q2 — month and year  (2 points)
    var q2 = form.addTextItem();
    q2.setTitle("What is the month and year?  e.g. April, 2026  (2 points)");
    q2.setRequired(true);

    // Q3 — special question for this whiteboard  (3 points)
    var q3 = form.addParagraphTextItem();
    q3.setTitle(wb.q3 + "  (3 points)");
    q3.setRequired(true);
  }

  // ── Link responses to a Google Sheet ──────────────────────────────────────
  var sheet = SpreadsheetApp.create("Whiteboard Quiz — Responses");
  form.setDestination(FormApp.DestinationType.SPREADSHEET, sheet.getId());

  // ── Log URLs ───────────────────────────────────────────────────────────────
  Logger.log("=================================================");
  Logger.log("Form created successfully!");
  Logger.log("Fill URL  : " + form.getPublishedUrl());
  Logger.log("Edit URL  : " + form.getEditUrl());
  Logger.log("Sheet URL : " + sheet.getUrl());
  Logger.log("=================================================");
}
