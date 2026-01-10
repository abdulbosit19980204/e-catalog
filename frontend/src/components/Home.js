import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { projectAPI, clientAPI, nomenklaturaAPI } from "../api";
import "./Home.css";

const extractItems = (response) => {
  if (!response?.data) return [];
  if (Array.isArray(response.data)) return response.data;
  if (Array.isArray(response.data.results)) return response.data.results;
  return [];
};

const extractCount = (response, fallbackLength) => {
  if (!response?.data) return fallbackLength || 0;
  if (typeof response.data.count === "number") return response.data.count;
  return fallbackLength || 0;
};

const toPlainText = (value) => {
  if (!value) return "";
  if (typeof value !== "string") return String(value);
  const withoutTags = value.replace(/<[^>]+>/g, " ");
  return withoutTags.replace(/\s+/g, " ").trim();
};

const Home = () => {
  const [stats, setStats] = useState({
    projects: 0,
    clients: 0,
    products: 0,
  });
  const [featured, setFeatured] = useState({
    projects: [],
    clients: [],
    products: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadOverview = async () => {
      try {
        setLoading(true);
        setError(null);
        const [projectsRes, clientsRes, productsRes] = await Promise.all([
          projectAPI.getProjects({ page_size: 4 }),
          clientAPI.getClients({ page_size: 6 }),
          nomenklaturaAPI.getNomenklatura({ page_size: 12 }),
        ]);

        const projectItems = extractItems(projectsRes);
        const clientItems = extractItems(clientsRes);
        const productItems = extractItems(productsRes);

        setFeatured({
          projects: projectItems,
          clients: clientItems,
          products: productItems,
        });

        setStats({
          projects: extractCount(projectsRes, projectItems.length),
          clients: extractCount(clientsRes, clientItems.length),
          products: extractCount(productsRes, productItems.length),
        });
      } catch (err) {
        console.error("Failed to load overview data", err);
        setError("Ma'lumotlarni yuklashda xatolik yuz berdi");
      } finally {
        setLoading(false);
      }
    };

    loadOverview();
  }, []);

  const heroStats = useMemo(
    () => [
      {
        label: "Projects",
        value: stats.projects,
        description: "Hamkor loyihalar bazasi",
        link: "/projects",
      },
      {
        label: "Clients",
        value: stats.clients,
        description: "Doimiy mijozlarimiz",
        link: "/clients",
      },
      {
        label: "Nomenklatura",
        value: stats.products,
        description: "Mahsulot katalogi",
        link: "/nomenklatura",
      },
    ],
    [stats]
  );

  const formatNumber = (value) => {
    if (!value) return "0";
    if (value < 1000) return value.toString();
    if (value < 10000) return value.toLocaleString("ru-RU");
    if (value < 1000000) return `${(value / 1000).toFixed(1)}k`;
    return `${(value / 1000000).toFixed(1)}m`;
  };

  const getPreviewImage = (entity) => {
    if (!entity?.images?.length) return null;
    const primary = entity.images[0];
    return (
      primary.image_main_url ||
      primary.image_md_url ||
      primary.image_sm_url ||
      primary.image_lg_url ||
      primary.image_url ||
      primary.image
    );
  };

  const heroProduct = useMemo(
    () => featured.products.find((item) => getPreviewImage(item)) || null,
    [featured.products]
  );

  const heroImage = heroProduct ? getPreviewImage(heroProduct) : null;

  return (
    <div className="home">
      <section className="hero">
        <div className="hero-inner">
          <div className="hero-copy">
            <div className="hero-badge">E-Catalog Market</div>
            <h1>
              <span>Zamonaviy katalog</span> — premium marketplace
            </h1>
            <p>
              Mahsulotlar, mijozlar va loyihalarni bir joyda boshqaring. Real vaqt rejimidagi
              yangilanishlar, qulay narxlar va ishonchli hamkorlik platformasi.
            </p>
            <div className="hero-actions">
              <Link to="/nomenklatura" className="btn primary">
                Katalogni ko‘rish
              </Link>
              <Link to="/clients" className="btn ghost">
                Mijozlar bazasi
              </Link>
            </div>
            <div className="hero-stats">
              {heroStats.map((item) => (
                <Link key={item.label} to={item.link} className="hero-stat-card">
                  <span className="stat-label">{item.label}</span>
                  <span className="stat-value">{formatNumber(item.value)}</span>
                  <span className="stat-description">{item.description}</span>
                </Link>
              ))}
            </div>
          </div>

          <div className="hero-media">
            {heroImage ? (
              <img src={heroImage} alt={heroProduct?.name || "Main product"} />
            ) : (
              <div className="hero-placeholder-alt">Katalog tasviri</div>
            )}
          </div>
        </div>
      </section>

      <section className="section projects">
        <div className="section-header">
          <div>
            <h2>Loyihalar vitrinasi</h2>
            <p>Eng so‘nggi va dolzarb loyihalarimiz</p>
          </div>
          <Link to="/admin/projects" className="link-button">
            Hammasi
          </Link>
        </div>

        <div className="project-feed">
          {featured.projects.map((project) => {
            const previewText = toPlainText(project.description);
            const truncatedText =
              previewText.length > 120
                ? `${previewText.slice(0, 120).trim()}...`
                : previewText;

            return (
              <article key={project.id} className="project-feed-item">
                <div className="project-thumb">
                  {getPreviewImage(project) ? (
                    <img src={getPreviewImage(project)} alt={project.name} />
                  ) : (
                    <div className="placeholder">Rasm yo‘q</div>
                  )}
                </div>
                <div className="project-content">
                  <h3>{project.name}</h3>
                  <p>{truncatedText || "Loyiha tavsifi mavjud emas"}</p>
                </div>
              </article>
            );
          })}
        </div>
      </section>

      <section className="section clients">
        <div className="section-header">
          <div>
            <h2>Mijozlar bazasi</h2>
            <p>Bizning ishonchli hamkorlarimiz</p>
          </div>
        </div>
        <div className="client-grid">
          {featured.clients.map((client) => (
            <div key={client.id} className="client-card">
              <div className="client-avatar">
                {getPreviewImage(client) ? (
                  <img src={getPreviewImage(client)} alt={client.name} />
                ) : (
                  <span>{client.name?.charAt(0)}</span>
                )}
              </div>
              <div className="client-info">
                <h3>{client.name}</h3>
                {client.city && <p>{client.city}</p>}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="section products">
        <div className="section-header">
          <div>
            <h2>Nomenklatura</h2>
            <p>Mahsulotlar katalogidan tanlanganlar</p>
          </div>
        </div>
        <div className="product-gallery">
          {featured.products.map((product) => (
            <div key={product.id} className="product-card">
              <div className="product-media">
                {getPreviewImage(product) ? (
                  <img src={getPreviewImage(product)} alt={product.name} />
                ) : (
                  <div className="placeholder">Rasm yo‘q</div>
                )}
              </div>
              <div className="product-body">
                <h3>{product.name}</h3>
              </div>
            </div>
          ))}
        </div>
      </section>

      <footer className="home-footer">
        <div className="footer-content">
          <p>© {new Date().getFullYear()} E-Catalog. Barcha huquqlar himoyalangan.</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;

