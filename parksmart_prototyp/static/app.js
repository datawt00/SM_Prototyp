'use strict';
const $ = (id) => document.getElementById(id);
const STORAGE = 'parksmart_bookings';
const saved = () => { try{return JSON.parse(localStorage.getItem(STORAGE) || '{}')}catch{return {}} };
function remember(day,spot){let all=saved();all[day]=spot;localStorage.setItem(STORAGE,JSON.stringify(all));}
function forget(day){let all=saved();delete all[day];localStorage.setItem(STORAGE,JSON.stringify(all));}
function message(text,err=false){$('message').textContent=text;$('message').className='message '+(err?'error':'ok')}
async function api(path, data){const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});const v=await r.json();if(!r.ok)throw Error(v.error||'Anfrage fehlgeschlagen');return v}
function buildSpot(p,day){
  const mine = saved()[day] === p.id;
  const card=document.createElement('div');card.className='spot '+(p.reserved?'booked':'');
  const symbol=document.createElement('div');symbol.className='symbol';symbol.textContent='🚗';card.append(symbol);
  const name=document.createElement('div');name.className='spot-name';name.textContent=p.id;card.append(name);
  const status=document.createElement('div');status.className='status';
  const dot=document.createElement('span');dot.className='dot';status.append(dot);
  const label=document.createElement('span');label.textContent=p.reserved?(mine?'Deine Reservierung':'Reserviert'):'Frei';status.append(label);card.append(status);
  const button=document.createElement('button');button.textContent=p.reserved?(mine?'Stornieren':'Nicht verfügbar'):'Reservieren';button.disabled=p.reserved&&!mine;
  if(mine && p.reserved){button.className='secondary';button.addEventListener('click',()=>cancel(day,p.id));}
  else if(!p.reserved){button.addEventListener('click',()=>book(day,p.id));}
  card.append(button);return card;
}
async function update(){
  try{
    const day=$('selected-date').value;
    if(!day)return;
    const r=await fetch('/api/state?date='+encodeURIComponent(day),{cache:'no-store'});
    const state=await r.json();if(!r.ok)throw Error(state.error||'Fehler');
    $('selected-date').min=state.today;$('selected-date').max=state.max_date;
    $('free-count').textContent=state.spots.length-state.reserved_count;
    $('booked-count').textContent=state.reserved_count;
    $('display-day').textContent=state.led_date+(state.preview_date?' (Demo-Vorschau)':' (heute)');
    $('hardware-mode').textContent=state.led_mode;
    $('spots').replaceChildren(...state.spots.map(p=>buildSpot(p,day)));
    $('leds').replaceChildren(...state.leds.map(p=>{const div=document.createElement('div');div.className='led-spot';const light=document.createElement('span');light.className='light '+(p.red?'red':'green');const name=document.createElement('span');name.textContent=p.id;div.append(light,name);return div}));
  }catch(e){message(e.message,true)}
}
async function book(day,spot){const owner=$('owner').value.trim();if(!owner)return message('Bitte zuerst ein Mitarbeiterkürzel eingeben.',true);try{const r=await api('/api/book',{date:day,spot,owner});remember(day,spot);message(r.message);update()}catch(e){message(e.message,true);update()}}
async function cancel(day,spot){const owner=$('owner').value.trim();if(!owner)return message('Bitte das Kürzel der ursprünglichen Buchung eintragen.',true);try{const r=await api('/api/cancel',{date:day,spot,owner});forget(day);message(r.message);update()}catch(e){message(e.message,true)}}
async function preview(date){try{const r=await api('/api/preview',{date});message(r.message);update()}catch(e){message(e.message,true)}}
async function reset(){if(!confirm('Wirklich alle Demo-Reservierungen löschen?'))return;try{const r=await api('/api/reset',{});localStorage.removeItem(STORAGE);message(r.message);update()}catch(e){message(e.message,true)}}
function isoLocal(d){return [d.getFullYear(),String(d.getMonth()+1).padStart(2,'0'),String(d.getDate()).padStart(2,'0')].join('-')}
const tomorrow=new Date();tomorrow.setDate(tomorrow.getDate()+1);$('selected-date').value=isoLocal(tomorrow);
$('owner').value=localStorage.getItem('parksmart_owner')||'';
$('owner').addEventListener('input',()=>localStorage.setItem('parksmart_owner',$('owner').value));
$('selected-date').addEventListener('change',update);
$('preview-button').addEventListener('click',()=>preview($('selected-date').value));
$('live-button').addEventListener('click',()=>preview(''));
$('reset-button').addEventListener('click',reset);
update();setInterval(update,4000);
