/* Presentation and localStorage data-access layer. Game rules live in battleship.py. */
"use strict";
const $ = id => document.getElementById(id);
const SAVE_KEY = 'battleship_final_game_v1';
const RECORD_KEY = 'battleship_final_records_v1';
let pyodide, gameState, records = [], lastWinnerSaved = false;
const symbol = {0:'',1:'◆',2:'•',3:'✕',4:'✖'};
const classes = {0:'',1:'ship',2:'miss',3:'hit',4:'sunk'};
function announce(message, error=false){$('message').textContent=message;$('message').style.borderColor=error?'#ef7f80':'#5be2d0';}
function call(request){
  const encoded=JSON.stringify(request);
  pyodide.globals.set('web_request',encoded);
  let response;
  try {response=JSON.parse(pyodide.runPython('battleship.api(web_request)'));}
  finally {pyodide.globals.delete('web_request');}
  if(!response.ok){announce(response.error,true);return null;}
  gameState=response.game;
  records=response.records;
  render(response.filtered);
  return response;
}
function persist(response){
  try {localStorage.setItem(SAVE_KEY,JSON.stringify(response.save));localStorage.setItem(RECORD_KEY,JSON.stringify(response.records));}
  catch(e){announce('บันทึกข้อมูลในเบราว์เซอร์ไม่ได้: '+e.message,true);}
}
function execute(request){
  if(!pyodide)return;
  const oldPhase=gameState?.phase;
  const response=call(request);
  if(!response)return;
  if(response.game.events.length){$('events').replaceChildren();response.game.events.slice(-12).forEach(item=>{
    const li=document.createElement('li');li.textContent=(item.actor==='computer'?'🤖 ':'')+
      (item.row ? `[${item.row},${item.col}] `:'')+item.message;$('events').append(li);
  });announce(response.game.events.at(-1).message);}
  if(response.game.phase==='finished'){
    announce(response.game.winner==='player'?'🏆 ชนะแล้ว! กองเรือศัตรูจมทั้งหมด':'💀 แพ้แล้ว! เรือของคุณถูกทำลายทั้งหมด');
    if(oldPhase!=='finished'&&!lastWinnerSaved){
      lastWinnerSaved=true;
      const name=$('player-name').value.trim()||'Captain';
      const record={id:crypto.randomUUID(),name:name.slice(0,24),turns:response.game.turn,
        result:response.game.winner==='player'?'win':'lose',date:new Date().toISOString()};
      const recorded=call({action:'records_add',record,...filters()});
      if(recorded)persist(recorded);else persist(response);
      return;
    }
  }
  persist(response);
}
function filters(){return {search:$('search').value,result:$('filter').value,order:$('sort').value};}
function renderBoard(id,grid,mode){
  const board=$(id);const frag=document.createDocumentFragment();
  const corner=document.createElement('span');corner.className='coord-label';frag.append(corner);
  for(let c=0;c<10;c++){const label=document.createElement('span');label.className='coord-label';label.textContent=c+1;frag.append(label);}
  for(let r=0;r<10;r++){
    const label=document.createElement('span');label.className='coord-label';label.textContent=r+1;frag.append(label);
    for(let c=0;c<10;c++){
      const value=grid[r][c],btn=document.createElement('button');btn.type='button';btn.className='cell '+classes[value];
      btn.textContent=symbol[value];btn.setAttribute('role','gridcell');btn.setAttribute('aria-label',`แถว ${r+1} คอลัมน์ ${c+1} ${['ยังไม่ยิง','เรือ','พลาด','โดน','จม'][value]}`);
      btn.disabled= mode==='place' ? (gameState.phase!=='setup'||value!==0) :
        (gameState.phase!=='battle'||value!==0);
      btn.addEventListener('click',()=>execute({action:mode==='place'?'place':'shoot',row:r,col:c,...filters()}));frag.append(btn);
    }
  }
  board.replaceChildren(frag);
}
function renderRecordList(items){
  const container=$('record-list');container.replaceChildren();
  if(!items.length){const p=document.createElement('p');p.className='empty';p.textContent='ยังไม่มีประวัติที่ตรงกับเงื่อนไข';container.append(p);return;}
  for(const item of items){
    const row=document.createElement('div');row.className='record-item';
    const info=document.createElement('div');info.className='record-text';
    const top=document.createElement('strong');top.textContent=`${item.result==='win'?'🏆':'⚓'} ${item.name}`;
    const bottom=document.createElement('small');bottom.textContent=`${item.turns} เทิร์น • ${item.date.slice(0,10)}`;
    info.append(top,bottom);
    const edit=document.createElement('button');edit.textContent='แก้ชื่อ';edit.type='button';edit.addEventListener('click',()=>{
      const name=prompt('ชื่อใหม่ (1–24 ตัวอักษร)',item.name);if(name===null)return;
      execute({action:'records_rename',id:item.id,name,...filters()});
    });
    const del=document.createElement('button');del.textContent='ลบ';del.type='button';del.addEventListener('click',()=>{
      if(confirm(`ลบประวัติของ ${item.name}?`))execute({action:'records_delete',id:item.id,...filters()});
    });row.append(info,edit,del);container.append(row);
  }
}
function render(filtered){
  $('phase').textContent=gameState.phase==='setup'?'วางกองเรือ':gameState.phase==='battle'?'กำลังรบ':'จบเกม';
  $('turn').textContent=gameState.turn;
  $('shots').textContent=gameState.phase==='battle'?gameState.shots_left:'—';
  $('ships').textContent=`${gameState.player_remaining} / ${gameState.enemy_remaining}`;
  $('placement-help').textContent=gameState.next_ship?
    `ลำดับ ${gameState.placed+1}/6: ${gameState.next_ship.name} (${gameState.next_ship.r} × ${gameState.next_ship.c}) — คลิกจุดเริ่มต้นของเรือ`:
    'วางเรือครบแล้ว! เล็งเป้าหมายบนกระดานศัตรู';
  $('auto-place').disabled=gameState.phase!=='setup';
  renderBoard('player-board',gameState.player_grid,'place');
  renderBoard('enemy-board',gameState.enemy_grid,'shoot');
  renderRecordList(filtered);
}
function readJson(storageKey){
  const content=localStorage.getItem(storageKey);
  if(!content)return null;
  try{return JSON.parse(content);}catch(e){announce('ไฟล์บันทึกในเบราว์เซอร์เสียหาย สามารถเริ่มเกมใหม่ได้',true);return null;}
}
function downloadJson(){
  const data={format:'battleship-final-backup-v1',game:readJson(SAVE_KEY),records};
  const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});
  const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='battleship-backup.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
async function uploadJson(event){
  const file=event.target.files?.[0];event.target.value='';if(!file)return;
  if(file.size>300000){announce('ไฟล์ใหญ่เกิน 300 KB',true);return;}
  try{
    const data=JSON.parse(await file.text());
    if(data.format!=='battleship-final-backup-v1'||!data.game||!Array.isArray(data.records))throw new Error('รูปแบบไฟล์ไม่ถูกต้อง');
    const oldGame=readJson(SAVE_KEY),oldRecords=JSON.parse(JSON.stringify(records));
    if(!call({action:'load',save:data.game,...filters()}))throw new Error('ข้อมูลเกมผิดรูปแบบ');
    if(!call({action:'records_load',records:data.records,...filters()})){
      call({action:'records_load',records:oldRecords,...filters()});
      if(oldGame)call({action:'load',save:oldGame,...filters()});
      else call({action:'new',...filters()});
      throw new Error('ข้อมูลคะแนนผิดรูปแบบ');
    }
    lastWinnerSaved=gameState.phase==='finished';
    persist(call({action:'state',...filters()}));announce('นำเข้า JSON สำเร็จ');
  }catch(e){announce(`ไม่สามารถนำเข้าได้: ${e.message}`,true);}
}
async function init(){
  try{
    pyodide=await loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v0.27.7/full/'});
    const res=await fetch('./battleship.py');if(!res.ok)throw new Error('ไม่พบ battleship.py');
    pyodide.FS.writeFile('/home/pyodide/battleship.py',await res.text());
    pyodide.runPython('import sys;sys.path.insert(0,"/home/pyodide");import battleship');
    const existing=readJson(SAVE_KEY);
    let response=existing?call({action:'load',save:existing,...filters()}):null;
    if(!response)response=call({action:'new',...filters()});
    const stored=readJson(RECORD_KEY);
    if(stored!==null&&!call({action:'records_load',records:stored,...filters()})){
      call({action:'records_load',records:[],...filters()});
      announce('ประวัติเก่ามีข้อผิดพลาด ระบบเริ่มรายการว่าง',true);
    }
    if(!existing)announce('พร้อมเล่น! คลิกวางเรือลำแรกหรือใช้ปุ่มสุ่มวางเรือ');
    else if(response)announce('โหลดสถานะเกมล่าสุดสำเร็จ');
    lastWinnerSaved=gameState.phase==='finished';
    ['new-game','restore','export'].forEach(id=>$(id).disabled=false);
    $('loader').textContent='● Python engine พร้อมใช้งาน (ประมวลผลภายในเบราว์เซอร์)';
  }catch(e){$('loader').textContent='⚠ โหลด Python ไม่สำเร็จ: '+e.message+' — ตรวจสอบอินเทอร์เน็ตหรือเปิดผ่านเว็บเซิร์ฟเวอร์';announce('ไม่สามารถเปิดเกมได้',true);}
}
$('new-game').addEventListener('click',()=>{if(confirm('เริ่มเกมใหม่? สถานะการรบปัจจุบันจะถูกแทนที่')){lastWinnerSaved=false;execute({action:'new',...filters()});announce('เกมใหม่เริ่มแล้ว กรุณาวางกองเรือ');}});
$('auto-place').addEventListener('click',()=>execute({action:'auto',...filters()}));
$('restore').addEventListener('click',()=>{const save=readJson(SAVE_KEY);if(!save){announce('ยังไม่มีข้อมูลบันทึก',true);return;}execute({action:'load',save,...filters()});lastWinnerSaved=gameState.phase==='finished';});
$('export').addEventListener('click',downloadJson);
$('import').addEventListener('change',uploadJson);
['search','filter','sort'].forEach(id=>$(id).addEventListener(id==='search'?'input':'change',()=>{if(pyodide)call({action:'records_query',...filters()});}));
init();
