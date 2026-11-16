import {readFile,mkdir,writeFile,rm,copyFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
await rm('dist',{recursive:true,force:true});await mkdir('dist/assets',{recursive:true});
const names={};
for(const file of ['styles.css','admin.css','behavior-metrics.js','app.js','admin.js']){
 let data=await readFile(`src/${file}`,'utf8');
 for(const [source,target]of Object.entries(names))data=data.replaceAll(`/src/${source}`,`/assets/${target}`);
 const hash=createHash('sha256').update(data).digest('hex').slice(0,10),name=file.replace('.',`.${hash}.`);names[file]=name;await writeFile(`dist/assets/${name}`,data);
}
for(const file of ['index.html','admin.html']){let html=await readFile(`src/${file}`,'utf8');for(const[source,target]of Object.entries(names))html=html.replaceAll(`/src/${source}`,`/assets/${target}`);await writeFile(`dist/${file}`,html);}
await copyFile('src/favicon.svg','dist/favicon.svg');await mkdir('../backend/app/static',{recursive:true});
for(const file of ['swagger-ui-bundle.js','swagger-ui.css'])await copyFile(`node_modules/swagger-ui-dist/${file}`,`../backend/app/static/${file}`);
console.log('Built public site, admin panel, telemetry module and local Swagger assets.');
