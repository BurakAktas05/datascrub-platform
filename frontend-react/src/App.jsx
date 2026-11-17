import { useRef, useState } from 'react';
import { ArrowDownToLine, ArrowRight, Check, FileSpreadsheet, LoaderCircle, Sparkles, Upload, X } from 'lucide-react';

const initialRules = {
  dropDuplicates: true,
  standardizeDates: true,
  numericFillStrategy: 'median',
  categoricalFillValue: 'Unknown',
  customNaValues: ['ERROR', 'UNKNOWN', 'N/A'],
  stripCurrencySymbols: [' TL', '$', '€'],
};

const number = (value) => new Intl.NumberFormat('tr-TR').format(value ?? 0);

export default function App() {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [rules, setRules] = useState(initialRules);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  function updateRule(key, value) {
    setRules((current) => ({ ...current, [key]: value }));
  }

  function chooseFile(nextFile) {
    setError('');
    setResult(null);
    if (!nextFile) return;
    if (!nextFile.name.toLowerCase().endsWith('.csv')) {
      setFile(null);
      setError('Lütfen .csv uzantılı bir dosya seç.');
      return;
    }
    setFile(nextFile);
  }

  async function processFile(event) {
    event.preventDefault();
    if (!file) {
      setError('Önce temizlemek istediğin CSV dosyasını ekle.');
      return;
    }

    setBusy(true);
    setError('');
    setResult(null);
    const body = new FormData();
    body.append('file', file);
    body.append('rules', new Blob([JSON.stringify(rules)], { type: 'application/json' }));

    try {
      const response = await fetch('/api/v1/scrub/process', { method: 'POST', body });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || data.title || 'Dosya işlenemedi. Servisleri kontrol edip tekrar dene.');
      setResult(data);
    } catch (err) {
      setError(err.message || 'Sunucuya bağlanılamadı.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="page-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="DataScrub ana sayfa">
          <span className="brand-icon"><Sparkles size={19} strokeWidth={2.2} /></span>
          <span>data<span className="brand-light">scrub</span></span>
        </a>
        <div className="engine-status"><span className="status-dot" /> Yerel çalışma alanı</div>
      </header>

      <section className="hero" id="top">
        <div className="eyebrow"><span /> DAHA TEMİZ VERİ, DAHA NET KARARLAR</div>
        <h1>CSV dosyanı<br /><span>temizle ve hazırla.</span></h1>
        <p className="hero-copy">Dosyanı ekle, temizlik kurallarını seç. Önizlemeyi gör ve düzenlenmiş verini indir.</p>
      </section>

      <form className="workspace" onSubmit={processFile}>
        <section className="panel upload-panel">
          <div className="section-heading">
            <div><span className="step-label">01 — DOSYAN</span><h2>CSV dosyanı ekle</h2></div>
            <span className="file-limit">CSV · Maks. 50 MB</span>
          </div>
          <input ref={inputRef} type="file" accept=".csv,text/csv" hidden onChange={(event) => chooseFile(event.target.files?.[0])} />
          <button className={`dropzone ${file ? 'has-file' : ''}`} type="button" onClick={() => inputRef.current?.click()} onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); chooseFile(event.dataTransfer.files?.[0]); }}>
            {file ? <><span className="upload-icon selected"><FileSpreadsheet size={23} /></span><span className="drop-title">{file.name}</span><span className="drop-subtitle">{(file.size / 1024 / 1024).toFixed(2)} MB · Başka dosya seçmek için tıkla</span></> : <><span className="upload-icon"><Upload size={22} /></span><span className="drop-title">Dosyanı buraya bırak</span><span className="drop-subtitle">veya <span className="browse-link">bilgisayarından seç</span></span></>}
          </button>
        </section>

        <section className="panel rules-panel">
          <div className="section-heading">
            <div><span className="step-label">02 — KURALLAR</span><h2>Temizlik seçenekleri</h2></div>
            <span className="defaults-label"><Sparkles size={13} /> Akıllı varsayılanlar</span>
          </div>
          <div className="rule-list">
            <label className="rule-row"><span><strong>Yinelenen satırları kaldır</strong><small>Aynı kayıtları tekilleştir</small></span><input type="checkbox" checked={rules.dropDuplicates} onChange={(e) => updateRule('dropDuplicates', e.target.checked)} /><i /></label>
            <label className="rule-row"><span><strong>Tarihleri standartlaştır</strong><small>Tarih değerlerini ortak biçime getir</small></span><input type="checkbox" checked={rules.standardizeDates} onChange={(e) => updateRule('standardizeDates', e.target.checked)} /><i /></label>
            <label className="rule-row select-row"><span><strong>Eksik sayısal değerler</strong><small>Boş hücreler için doldurma yöntemi</small></span><select value={rules.numericFillStrategy} onChange={(e) => updateRule('numericFillStrategy', e.target.value)}><option value="median">Ortanca değer</option><option value="mean">Ortalama</option><option value="drop">Satırı kaldır</option></select></label>
          </div>
          <button className="process-button" type="submit" disabled={busy}>{busy ? <><LoaderCircle className="spin" size={17} /> Dosya temizleniyor</> : <>Veriyi temizle <ArrowRight size={17} /></>}</button>
          {error && <div className="error-message"><X size={16} />{error}</div>}
        </section>
      </form>

      {result && <section className="panel result-panel">
        <div className="result-heading"><div><span className="step-label">TAMAMLANDI</span><h2><span className="success-icon"><Check size={16} /></span> Dosyan hazır</h2></div><a className="download-button" href={`/api/v1/scrub/download/${encodeURIComponent(result.jobId)}`}><ArrowDownToLine size={17} /> CSV indir</a></div>
        <div className="stats-grid"><div><small>İşlenen satır</small><strong>{number(result.stats?.rowsBefore)}</strong></div><div><small>Sonuç satırı</small><strong>{number(result.stats?.rowsAfter)}</strong></div><div><small>Kaldırılan kopya</small><strong>{number(result.stats?.duplicatesRemoved)}</strong></div><div><small>İşlem süresi</small><strong>{number(result.stats?.processingTimeMs)}<em> ms</em></strong></div></div>
        {result.previewRows?.length > 0 && <div className="preview-wrap"><h3>İlk satırlardan önizleme</h3><div className="table-scroll"><table><thead><tr>{Object.keys(result.previewRows[0]).map((key) => <th key={key}>{key}</th>)}</tr></thead><tbody>{result.previewRows.map((row, index) => <tr key={index}>{Object.values(row).map((value, cell) => <td key={cell}>{value == null ? '—' : String(value)}</td>)}</tr>)}</tbody></table></div></div>}
      </section>}

      <footer>Dosyaların bu yerel çalışma alanında işlenir. Yüklemeden önce CSV içeriğini kontrol et.</footer>
    </main>
  );
}
