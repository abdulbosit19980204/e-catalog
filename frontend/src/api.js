import axios from "axios";

let derivedApiBase = process.env.REACT_APP_API_URL;
if (!derivedApiBase && typeof window !== "undefined") {
  const origin = window.location.origin.replace(/\/$/, "");
  derivedApiBase = `${origin}/api/v1`;
}
const API_BASE_URL = derivedApiBase || "http://localhost:8000/api/v1";

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
};

// Client API
export const clientAPI = {
  getClients: (params = {}) => {
    return apiClient.get("/client/", { params });
  },
  getClient: (clientCode1c) => {
    return apiClient.get(`/client/${clientCode1c}/`);
  },
  createClient: (data) => {
    return apiClient.post("/client/", data);
  },
  updateClient: (clientCode1c, data) => {
    return apiClient.patch(`/client/${clientCode1c}/`, data);  // PATCH ishlatish
  },
  deleteClient: (clientCode1c) => {
    return apiClient.delete(`/client/${clientCode1c}/`);
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
};

// Nomenklatura API
export const nomenklaturaAPI = {
  getNomenklatura: (params = {}) => {
    return apiClient.get("/nomenklatura/", { params });
  },
  getNomenklaturaItem: (code1c) => {
    return apiClient.get(`/nomenklatura/${code1c}/`);
  },
  createNomenklatura: (data) => {
    return apiClient.post("/nomenklatura/", data);
  },
  updateNomenklatura: (code1c, data) => {
    return apiClient.patch(`/nomenklatura/${code1c}/`, data);  // PATCH ishlatish
  },
  deleteNomenklatura: (code1c) => {
    return apiClient.delete(`/nomenklatura/${code1c}/`);
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
};

export default apiClient;
