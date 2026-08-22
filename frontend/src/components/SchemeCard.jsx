function SchemeCard({ scheme }) {
  return (
    <div className="scheme-card">
      <div className="scheme-card-header">
        <span className="scheme-badge">
          Government Scheme
        </span>

        {scheme.short_name && (
          <span className="scheme-short-name">
            {scheme.short_name}
          </span>
        )}
      </div>

      <h3>{scheme.name}</h3>


      {scheme.official_source && (
        <a
          href={scheme.official_source}
          target="_blank"
          rel="noopener noreferrer"
          className="scheme-link"
        >
          View official source →
        </a>
      )}
    </div>
  );
}

export default SchemeCard;