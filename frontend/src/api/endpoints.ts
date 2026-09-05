import { apiClient } from "./client";

// Health & System Diagnostics
export const getHealth = () => apiClient("/health");
export const getDiagnostics = () => apiClient("/diagnostics");

// Courses
export const listCourses = (studentId = "stu_cit_ad5305_001") =>
  apiClient("/courses?student_id=" + encodeURIComponent(studentId));

export const getCourseDashboard = (courseId: string) =>
  apiClient("/courses/" + encodeURIComponent(courseId) + "/dashboard");

export const createCourse = (payload: any) =>
  apiClient("/courses", { method: "POST", body: JSON.stringify(payload) });

// Student Platform Dashboard
export const getStudentDashboard = (studentId = "stu_cit_ad5305_001") =>
  apiClient("/students/" + encodeURIComponent(studentId) + "/dashboard");

// Ask Teacher & Doubts
export const askTeacher = (
  studentId: string,
  payload: { question?: string; doubt_text?: string; course_id?: string; context?: any; timestamp?: number }
) => {
  const text = payload.doubt_text || payload.question || "";
  return apiClient("/students/" + encodeURIComponent(studentId) + "/ask-teacher", {
    method: "POST",
    body: JSON.stringify({
      ...payload,
      doubt_text: text,
      question: text,
    }),
  });
};

export const listDoubts = (studentId = "stu_cit_ad5305_001") =>
  apiClient("/students/" + encodeURIComponent(studentId) + "/doubts");

export const updateDoubtStatus = (doubtId: string, status: string) =>
  apiClient("/doubts/" + encodeURIComponent(doubtId) + "/status", {
    method: "PUT",
    body: JSON.stringify({ status }),
  });

// Pedagogical Teaching Controls & Timestamp Interrupt/Resume
export const executeTeachingControl = (
  studentId: string,
  action: "simpler" | "deep_dive" | "faster" | "slower" | "give_hint" | "switch_language",
  params: Record<string, any> = {}
) =>
  apiClient("/students/" + encodeURIComponent(studentId) + "/teaching-session/control", {
    method: "POST",
    body: JSON.stringify({
      action,
      params,
      concept: params.concept,
      context: params.context,
    }),
  });

export const interruptTeachingSession = (
  studentId: string,
  payload: {
    session_id?: string;
    lesson_id?: string;
    timestamp_seconds?: number;
    paused_timestamp?: number;
    topic?: string;
    current_concept?: string;
    doubt_text?: string;
    question?: string;
  }
) => {
  const timestamp = payload.paused_timestamp ?? payload.timestamp_seconds ?? 0;
  const doubt = payload.doubt_text || payload.question || "Student interrupted lesson to clarify concept.";
  return apiClient("/students/" + encodeURIComponent(studentId) + "/teaching-session/interrupt", {
    method: "POST",
    body: JSON.stringify({
      ...payload,
      session_id: payload.session_id || payload.lesson_id || `session_${studentId}`,
      paused_timestamp: timestamp,
      timestamp_seconds: timestamp,
      current_concept: payload.current_concept || payload.topic || "Core Concept",
      doubt_text: doubt,
    }),
  });
};

export const resumeTeachingSession = (
  studentId: string,
  payload: { session_id?: string; lesson_id?: string }
) =>
  apiClient("/students/" + encodeURIComponent(studentId) + "/teaching-session/resume", {
    method: "POST",
    body: JSON.stringify(payload),
  });

// Practical Learning
export const listPracticalTasks = (studentId = "stu_cit_ad5305_001", subject?: string) => {
  const query = subject ? "?subject=" + encodeURIComponent(subject) : "";
  return apiClient("/students/" + encodeURIComponent(studentId) + "/practical-tasks" + query);
};

export const generatePracticalTask = (studentId: string, subject: string) =>
  apiClient("/students/" + encodeURIComponent(studentId) + "/practical-tasks", {
    method: "POST",
    body: JSON.stringify({ subject }),
  });

export const evaluatePracticalTask = (
  studentId: string,
  taskId: string,
  codeSubmission: string
) =>
  apiClient(
    "/students/" +
      encodeURIComponent(studentId) +
      "/practical-tasks/" +
      encodeURIComponent(taskId) +
      "/evaluate",
    {
      method: "POST",
      body: JSON.stringify({ code: codeSubmission, code_submission: codeSubmission }),
    }
  );

// Exam Plans & Revision
export const listExamPlans = (studentId = "stu_cit_ad5305_001") =>
  apiClient("/students/" + encodeURIComponent(studentId) + "/exam-plans");

export const generateExamPlan = (studentId: string, payload: any) =>
  apiClient("/students/" + encodeURIComponent(studentId) + "/exam-plans", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const replanExam = (planId: string, payload: any) =>
  apiClient("/exam-plans/" + encodeURIComponent(planId) + "/replan", {
    method: "POST",
    body: JSON.stringify(payload),
  });

// Analytics & Mentor Reports
export const getStudentAnalytics = (studentId = "stu_cit_ad5305_001") =>
  apiClient("/students/" + encodeURIComponent(studentId) + "/analytics");

export const getMentorReport = (studentId = "stu_cit_ad5305_001") =>
  apiClient("/students/" + encodeURIComponent(studentId) + "/mentor-report");

export const getCrossCourseGraph = (studentId = "stu_cit_ad5305_001") =>
  apiClient("/students/" + encodeURIComponent(studentId) + "/cross-course-graph");

// Canonical College Demo Flows
export const runMlCourseDemo = (payload: { unit?: number; concept?: string; student_id?: string } = {}) =>
  apiClient("/demo/run-ml-course", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const runOhmsLawDemo = () =>
  apiClient("/demo/run-ohms-law", {
    method: "POST",
    body: JSON.stringify({}),
  });

// Documents & Ingestion
export const listDocuments = (studentId = "stu_cit_ad5305_001") =>
  apiClient("/documents?student_id=" + encodeURIComponent(studentId));

export const uploadDocument = (formData: FormData) =>
  apiClient("/documents/pipeline-upload", {
    method: "POST",
    body: formData,
  });

export const processDocument = (documentId: string) =>
  apiClient("/documents/process", {
    method: "POST",
    body: JSON.stringify({ document_id: documentId }),
  });

export const getDocumentStatus = (documentId: string) =>
  apiClient("/documents/" + encodeURIComponent(documentId) + "/status");

export const searchRag = (query: string, courseId?: string) =>
  apiClient("/rag/search", {
    method: "POST",
    body: JSON.stringify({ query, course_id: courseId }),
  });

// Lesson Flow, Assessments & Misconceptions
export const startLesson = (lessonId: string, payload: any = {}) =>
  apiClient("/lessons/" + encodeURIComponent(lessonId) + "/start", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const getLessonState = (lessonId: string) =>
  apiClient("/lessons/" + encodeURIComponent(lessonId) + "/state");

export const advanceLessonNextAction = (lessonId: string) =>
  apiClient("/lessons/" + encodeURIComponent(lessonId) + "/next-action", {
    method: "POST",
    body: JSON.stringify({}),
  });

export const getCheckpointQuestion = (lessonId: string, payload: any = {}) =>
  apiClient("/lessons/" + encodeURIComponent(lessonId) + "/question", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const evaluateStudentAnswer = (lessonId: string, payload: any) =>
  apiClient("/lessons/" + encodeURIComponent(lessonId) + "/answer", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const triggerAdaptiveReteach = (lessonId: string, payload: any = {}) =>
  apiClient("/lessons/" + encodeURIComponent(lessonId) + "/adapt", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const getStudentMisconceptions = (studentId = "stu_cit_ad5305_001") =>
  apiClient("/students/" + encodeURIComponent(studentId) + "/misconceptions");

// Learner Profile
export const getLearnerProfile = (learnerId = "stu_cit_ad5305_001") =>
  apiClient("/learners/" + encodeURIComponent(learnerId) + "/profile");

export const saveLearnerProfile = (payload: any) =>
  apiClient("/learners/profile", {
    method: "POST",
    body: JSON.stringify(payload),
  });

// Realtime RTC & Media
export const getAgoraCredentials = (channel: string, uid: number) =>
  apiClient("/realtime/agora/credentials", {
    method: "POST",
    body: JSON.stringify({ channel, uid, role: "publisher" }),
  });

export const listTeachers = () => apiClient("/media/teachers");

export const selectTeacher = (teacherId: string) =>
  apiClient("/media/teacher/select", {
    method: "POST",
    body: JSON.stringify({ teacher_id: teacherId }),
  });

export const uploadCourseDocument = async (file: File, courseId = "machine-learning", studentId = "stu_cit_ad5305_001") => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("course", courseId);
  formData.append("student_id", studentId);
  return apiClient("/documents/pipeline-upload", {
    method: "POST",
    body: formData,
  });
};

export const api = {
  getHealth,
  getDiagnostics,
  listCourses,
  getCourseDashboard,
  createCourse,
  getStudentDashboard,
  askTeacher,
  listDoubts,
  updateDoubtStatus,
  executeTeachingControl,
  interruptTeachingSession,
  resumeTeachingSession,
  listPracticalTasks,
  generatePracticalTask,
  evaluatePracticalTask,
  listExamPlans,
  generateExamPlan,
  replanExam,
  getStudentAnalytics,
  getMentorReport,
  getCrossCourseGraph,
  runMlCourseDemo,
  runOhmsLawDemo,
  listDocuments,
  uploadDocument,
  uploadCourseDocument,
  processDocument,
  getDocumentStatus,
  searchRag,
  startLesson,
  getLessonState,
  advanceLessonNextAction,
  getCheckpointQuestion,
  evaluateStudentAnswer,
  triggerAdaptiveReteach,
  getStudentMisconceptions,
  getLearnerProfile,
  saveLearnerProfile,
  getAgoraCredentials,
  listTeachers,
  selectTeacher,
};
