<group class="radiogroup" ng-if="asideFormData.ui_isInoutwater == true">
    <header>{{::"DUPLICATE.302"|translate}}</header>
    <controls>
		<radio-button ng-model="asideFormData.oper" value="ON" bind-title="::'DUPLICATE.11'|translate" use-toggle></radio-button>
		<radio-button ng-model="asideFormData.oper" value="OFF" bind-title="::'DUPLICATE.12'|translate" use-toggle></radio-button>
    </controls>
</group>
<group class="radiogroup radiogroup-mode radiogroup-awhpmode" ng-if="asideFormData.ui_isInoutwater == true">
	<header>
		{{::"DUPLICATE.369"|translate}}
	</header>
	<controls>
		<radio-button ng-model="asideFormData.mode" bind-value="'COOL'" bind-title="::'VALUETYPES.AWHP_MODE.COOL' | translate" ng-click="clickAwhpMode(asideFormData)"
					  ng-disabled="asideFormData.type == 'HEAT_ONLY_AWHP' || asideFormData.type == 'CASCADE'"></radio-button>
		<radio-button ng-model="asideFormData.mode" bind-value="'HEAT'" bind-title="::'VALUETYPES.AWHP_MODE.HEAT' | translate" ng-click="clickAwhpMode(asideFormData)"></radio-button>
		<radio-button ng-model="asideFormData.mode" bind-value="'AUTO'" bind-title="::'VALUETYPES.AWHP_MODE.AUTO' | translate" ng-click="clickAwhpMode(asideFormData)"></radio-button>
	</controls>
</group>
<group class="steppergroup" ng-if="asideFormData.ui_isInoutwater == true && asideFormData.wotemp_flag == 'OFF'">
	<!--공기온도-->
	<header>
		{{::"HISTORY_CONTROL.AWHP.AIRSETTEMP"|translate}}
	</header>
	<controls>
		<stepper ng-model="asideFormData.settemp" step="1" min="asideFormData.inoutwater_air_temp_min" max="asideFormData.inoutwater_air_temp_max" unit="{{::gTempUnit}}"></stepper>
	</controls>
</group>
<group class="steppergroup" ng-if="asideFormData.ui_isInoutwater == true && asideFormData.wotemp_flag == 'ON'">
	<!--입출수 온도-->
	<header>
		{{::"DUPLICATE.428"|translate}}
	</header>
	<controls>
		<stepper ng-if="asideFormData.mode != null" ng-model="asideFormData.settemp" step="1" steppress="10" min="asideFormData.inoutwater_air_temp_min" max="asideFormData.inoutwater_air_temp_max" unit="{{::gTempUnit}}"></stepper>
		<stepper ng-if="asideFormData.mode == undefined" ng-model="asideFormData.settemp" step="1" steppress="10" min="5" max="80" unit="{{::gTempUnit}}" disabled></stepper>
	</controls>
</group>
<group class="radiogroup" ng-if="asideFormData.ui_isHotwater == true">
    <header>{{::"HISTORY_CONTROL.AWHP.HOTWATER"|translate}}</header>
    <controls>
		<radio-button ng-model="asideFormData.hotw_oper" value="ON" bind-title="::'DUPLICATE.11'|translate" use-toggle></radio-button>
		<radio-button ng-model="asideFormData.hotw_oper" value="OFF" bind-title="::'DUPLICATE.12'|translate" use-toggle></radio-button>
    </controls>
</group>
<group class="steppergroup" ng-if="asideFormData.ui_isHotwater == true">
	<!--온수온도-->
	<header>
		{{::"DUPLICATE.92"|translate}}
	</header>
	<controls>
		<stepper ng-model="asideFormData.wt_settemp" step="1" steppress="10" min="asideFormData.hotwater_temp_min" max="asideFormData.hotwater_temp_max" unit="{{::gTempUnit}}"></stepper>
	</controls>
</group>
<group class="radiogroup">
	<header>
		{{::"DUPLICATE.321"|translate}}
	</header>
	<controls ng-disabled="systems.lgap_type == 'SLAVE'">
		<radio-button ng-model="asideFormData.lock" value="ON" bind-title="::'DUPLICATE.23'|translate" ></radio-button>
		<radio-button ng-model="asideFormData.lock" value="OFF" bind-title="::'DUPLICATE.24'|translate" ></radio-button>
	</controls>
</group>
