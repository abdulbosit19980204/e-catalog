import axios from "axios";

let derivedApiBase = process.env.REACT_APP_API_URL;
if (!derivedApiBase && typeof window !== "undefined") {
  const { protocol, hostname, port } = window.location;
  const isLocal = hostname === "localhost" || hostname === "127.0.0.1";
  
  if (isLocal) {
    const isDevPort = port === "3000" || port === "5173";
    if (isDevPort) {
      derivedApiBase = `${protocol}//${hostname}:8000/api/v1`;
    } else {
      derivedApiBase = `${protocol}//${hostname}:${port}/api/v1`;
    }
  }
}
const API_BASE_URL = derivedApiBase || "http://178.218.200.120:1596/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Token saqlash va qo'shish
let authToken = localStorage.getItem("authToken");
const dispatchAuthEvent = () => {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event("auth-token-changed"));
  }
};
if (authToken) {
  apiClient.defaults.headers.common["Authorization"] = `Bearer ${authToken}`;
}

// Token yangilash
export const setAuthToken = (token) => {
  if (token) {
    isAuthRedirectScheduled = false;
  }
  authToken = token;
  if (token) {
    localStorage.setItem("authToken", token);
    apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    dispatchAuthEvent();
  } else {
    localStorage.removeItem("authToken");
    delete apiClient.defaults.headers.common["Authorization"];
    dispatchAuthEvent();
  }
};

let isAuthRedirectScheduled = false;
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const { response } = error || {};
    if (response && [401, 403].includes(response.status)) {
      setAuthToken(null);
      localStorage.removeItem("refreshToken");
      sessionStorage.removeItem("authToken");

      if (typeof window !== "undefined" && !isAuthRedirectScheduled) {
        isAuthRedirectScheduled = true;
        const currentPath = window.location.pathname || "";
        const loginPath = "/login";
        if (!currentPath.startsWith(loginPath)) {
          const searchParams = new URLSearchParams({ reason: "session_expired" });
          window.location.replace(`${loginPath}?${searchParams.toString()}`);
        } else {
          isAuthRedirectScheduled = false;
        }
      }
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: (username, password) => {
    return axios.post(`${API_BASE_URL.replace("/v1", "")}/token/`, {
      username,
      password,
    });
  },
  refreshToken: (refresh) => {
    return axios.post(`${API_BASE_URL.replace("/v1", "")}/token/refresh/`, {
      refresh,
    });
  },
  verifyToken: (token) => {
    return axios.post(`${API_BASE_URL.replace("/v1", "")}/token/verify/`, {
      token,
    });
  },
};

// Project API
export const projectAPI = {
  getProjects: (params = {}) => {
    return apiClient.get("/project/", { params });
  },
  getProject: (code1c) => {
    return apiClient.get(`/project/${code1c}/`);
  },
  createProject: (data) => {
    return apiClient.post("/project/", data);
  },
  updateProject: (code1c, data) => {
    return apiClient.patch(`/project/${code1c}/`, data);  // PATCH ishlatish - faqat o'zgargan field'larni yuborish
  },
  deleteProject: (code1c) => {
    return apiClient.delete(`/project/${code1c}/`);
  },
  // Image upload
  uploadImage: (projectCode, imageFile, options = {}) => {
    const formData = new FormData();
    formData.append('project', projectCode);
    formData.append('image', imageFile);
    if (options.category !== undefined) {
      formData.append('category', options.category);
    }
    if (options.note !== undefined) {
      formData.append('note', options.note);
    }
    return apiClient.post("/project-image/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  bulkUploadImages: (projectCode, imageFiles, options = {}) => {
    const formData = new FormData();
    formData.append('project', projectCode);
    if (options.category !== undefined) {
      formData.append('category', options.category);
    }
    if (options.note !== undefined) {
      formData.append('note', options.note);
    }
    imageFiles.forEach((file) => {
      formData.append('images', file);
    });
    return apiClient.post("/project-image/bulk-upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  getProjectImages: (projectCode) => {
    return apiClient.get("/project-image/", { params: { project: projectCode } });
  },
  deleteImage: (imageId) => {
    return apiClient.delete(`/project-image/${imageId}/`);
  },
  setMainImage: (imageId) => {
    return apiClient.patch(`/project-image/${imageId}/`, { is_main: true });
  },
};

// Client API
export const clientAPI = {
  getClients: (params = {}) => {
    return apiClient.get("/client/", { params });
  },
  getClient: (clientCode1c, project_id) => {
    return apiClient.get(`/client/${clientCode1c}/`, { params: { project_id } });
  },

  createClient: (data) => {
    return apiClient.post("/client/", data);
  },
  updateClient: (clientCode1c, data, project_id) => {
    return apiClient.patch(`/client/${clientCode1c}/`, data, { params: { project_id } });
  },
  deleteClient: (clientCode1c, project_id) => {
    return apiClient.delete(`/client/${clientCode1c}/`, { params: { project_id } });
  },
  importClients: (file, project_id) => {
    const formData = new FormData();
    formData.append('file', file);
    if (project_id) {
      formData.append('project_id', project_id);
    }
    return apiClient.post("/client/import-xlsx/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  // Image upload
  uploadImage: (clientCode, imageFile, options = {}) => {
    const formData = new FormData();
    formData.append('client', clientCode);
    formData.append('image', imageFile);
    if (options.category !== undefined) {
      formData.append('category', options.category);
    }
    if (options.note !== undefined) {
      formData.append('note', options.note);
    }
    return apiClient.post("/client-image/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  bulkUploadImages: (clientCode, imageFiles, options = {}) => {
    const formData = new FormData();
    formData.append('client', clientCode);
    if (options.category !== undefined) {
      formData.append('category', options.category);
    }
    if (options.note !== undefined) {
      formData.append('note', options.note);
    }
    if (options.project_id) {
      formData.append('project_id', options.project_id);
    }
    imageFiles.forEach((file) => {
      formData.append('images', file);
    });

    return apiClient.post("/client-image/bulk-upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  getClientImages: (clientCode) => {
    return apiClient.get("/client-image/", { params: { client: clientCode } });
  },
  deleteImage: (imageId) => {
    return apiClient.delete(`/client-image/${imageId}/`);
  },
  setMainImage: (imageId) => {
    return apiClient.patch(`/client-image/${imageId}/`, { is_main: true });
  },
};

// Nomenklatura API
export const nomenklaturaAPI = {
  getNomenklatura: (params = {}) => {
    return apiClient.get("/nomenklatura/", { params });
  },
  getNomenklaturaItem: (code1c, project_id) => {
    return apiClient.get(`/nomenklatura/${code1c}/`, { params: { project_id } });
  },
  createNomenklatura: (data) => {
    return apiClient.post("/nomenklatura/", data);
  },
  updateNomenklatura: (code1c, data, project_id) => {
    return apiClient.patch(`/nomenklatura/${code1c}/`, data, { params: { project_id } });
  },
  deleteNomenklatura: (code1c, project_id) => {
    return apiClient.delete(`/nomenklatura/${code1c}/`, { params: { project_id } });
  },
  importNomenklatura: (file, project_id) => {
    const formData = new FormData();
    formData.append('file', file);
    if (project_id) {
      formData.append('project_id', project_id);
    }
    return apiClient.post("/nomenklatura/import-xlsx/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  exportNomenklatura: (params = {}) => {
    return apiClient.get("/nomenklatura/export-xlsx/", { params, responseType: 'blob' });
  },

  // Image upload
  uploadImage: (nomenklaturaCode, imageFile, options = {}) => {
    const formData = new FormData();
    formData.append('nomenklatura', nomenklaturaCode);
    formData.append('image', imageFile);
    if (options.category !== undefined) {
      formData.append('category', options.category);
    }
    if (options.note !== undefined) {
      formData.append('note', options.note);
    }
    return apiClient.post("/nomenklatura-image/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  bulkUploadImages: (nomenklaturaCode, imageFiles, options = {}) => {
    const formData = new FormData();
    formData.append('nomenklatura', nomenklaturaCode);
    if (options.category !== undefined) {
      formData.append('category', options.category);
    }
    if (options.note !== undefined) {
      formData.append('note', options.note);
    }
    if (options.project_id) {
      formData.append('project_id', options.project_id);
    }
    imageFiles.forEach((file) => {
      formData.append('images', file);
    });

    return apiClient.post("/nomenklatura-image/bulk-upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  getNomenklaturaImages: (nomenklaturaCode) => {
    return apiClient.get("/nomenklatura-image/", { params: { nomenklatura: nomenklaturaCode } });
  },
  deleteImage: (imageId) => {
    return apiClient.delete(`/nomenklatura-image/${imageId}/`);
  },
  setMainImage: (imageId) => {
    return apiClient.patch(`/nomenklatura-image/${imageId}/`, { is_main: true });
  },
};

// User Management API
export const userAPI = {
  getUsers: (params = {}) => {
    return apiClient.get("/users/", { params });
  },
  createUser: (data) => {
    return apiClient.post("/users/", data);
  },
  updateUser: (id, data) => {
    return apiClient.patch(`/users/${id}/`, data);
  },
  deleteUser: (id) => {
    return apiClient.delete(`/users/${id}/`);
  },
};

// Integration API
export const integrationAPI = {
  getIntegrations: () => {
    return apiClient.get("/integration/");
  },
  syncNomenklatura: (integrationId) => {
    return apiClient.post(`/integration/sync/nomenklatura/${integrationId}/`);
  },
  syncClients: (integrationId) => {
    return apiClient.post(`/integration/sync/clients/${integrationId}/`);
  },
  getSyncStatus: (taskId) => {
    return apiClient.get(`/integration/sync/status/${taskId}/`);
  },
  getHistory: (params = {}) => {
    return apiClient.get("/integration/history/", { params });
  },
};

// Chat API
export const chatAPI = {
  getSettings: () => {
    return apiClient.get("/chat/settings/current/");
  },
  updateSettings: (id, data) => {
    return apiClient.patch(`/chat/settings/${id}/`, data);
  },
  getConversations: (params = {}) => {
    return apiClient.get("/chat/conversations/", { params });
  },
  createConversation: (data) => {
    return apiClient.post("/chat/conversations/", data);
  },
  closeConversation: (id) => {
    return apiClient.patch(`/chat/conversations/${id}/`, { status: 'closed' });
  },
  getMessages: (conversationId) => {
    return apiClient.get(`/chat/conversations/${conversationId}/messages/`);
  },
  sendMessage: (data) => {
    if (data instanceof FormData) {
      return apiClient.post("/chat/messages/", data, {
        headers: { "Content-Type": "multipart/form-data" },
      });
    }
    return apiClient.post("/chat/messages/", data);
  },
};

// Agent Location API
export const agentLocationAPI = {
  getLocations: (params = {}) => {
    return apiClient.get("/agent-location/", { params });
  },
  getUniqueAgents: () => {
    return apiClient.get("/agent-location/unique-agents/");
  },
  getTrajectory: (agentCode, date) => {
    return apiClient.get("/agent-location/trajectory/", {
      params: { agent_code: agentCode, date }
    });
  },
  deleteLocation: (id) => {
    return apiClient.delete(`/agent-location/${id}/`);
  }
};

export default apiClient;
