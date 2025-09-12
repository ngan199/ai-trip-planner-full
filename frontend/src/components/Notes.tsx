// Purpose: Render backend notes/uncertainties to improve transparency (explainability)
export default function Notes({ notes, uncertainties }: { notes?: string[]; uncertainties?: string[] }) {
  if ((!notes || notes.length === 0) && (!uncertainties || uncertainties.length === 0)) return null;
  return (
    <div style={{ marginTop: 12, border: "1px dashed #ccc", padding: 10, borderRadius: 8 }}>
      {notes && notes.length > 0 && (
        <>
          <strong>Notes</strong>
          <ul style={{ marginTop: 6 }}>
            {notes.map((n, i) => <li key={i}>{n}</li>)}
          </ul>
        </>
      )}
      {uncertainties && uncertainties.length > 0 && (
        <>
          <strong>Uncertainties</strong>
          <ul style={{ marginTop: 6 }}>
            {uncertainties.map((u, i) => <li key={i}>{u}</li>)}
          </ul>
        </>
      )}
    </div>
  );
}
