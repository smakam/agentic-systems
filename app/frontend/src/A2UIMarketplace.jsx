import React from 'react';
import {createComponentImplementation} from '@a2ui/react';
import {CommonSchemas,basicCatalog} from '@a2ui/web_core/v1_0';
import {z} from 'zod';
import {displayCatalogId} from './a2ui.js';

import {OrderSummary,RecordTable,EventTimeline} from './MarketplaceViews.jsx';
const domain=(name,prop,view)=>createComponentImplementation({name,schema:z.object({[prop]:CommonSchemas.DynamicValue})},({props})=>React.createElement(view,props));
export const marketplaceCatalog=basicCatalog.derive({catalogId:displayCatalogId,components:['Column','Row','Card','Text','Divider','Button',domain('OrderSummary','record',OrderSummary),domain('RecordTable','dataset',RecordTable),domain('EventTimeline','dataset',EventTimeline)],functions:[]});
