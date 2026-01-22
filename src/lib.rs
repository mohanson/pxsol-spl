#![allow(unexpected_cfgs)]

solana_program::entrypoint!(process_instruction);

pub fn process_instruction(
    _: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    _: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let account_user = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_user_spla = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_mana = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_mana_auth = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_mana_spla = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_mint = solana_program::account_info::next_account_info(accounts_iter)?;
    let _ = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_spl = solana_program::account_info::next_account_info(accounts_iter)?;
    let _ = solana_program::account_info::next_account_info(accounts_iter)?;

    assert!(account_user.is_signer);
    let account_user_spla_calc = spl_associated_token_account::get_associated_token_address_with_program_id(
        &account_user.key,
        &account_mint.key,
        &spl_token_2022::id(),
    );
    assert_eq!(account_user_spla.key, &account_user_spla_calc);
    let account_mana_auth_calc = solana_program::pubkey::Pubkey::find_program_address(&[&[]], account_mana.key);
    assert_eq!(account_mana_auth.key, &account_mana_auth_calc.0);
    let account_mana_spla_calc = spl_associated_token_account::get_associated_token_address_with_program_id(
        &account_mana_auth.key,
        &account_mint.key,
        &spl_token_2022::id(),
    );
    assert_eq!(account_mana_spla.key, &account_mana_spla_calc);
    assert_eq!(account_spl.key, &spl_token_2022::id());

    solana_program::program::invoke(
        &spl_associated_token_account::instruction::create_associated_token_account_idempotent(
            &account_user.key,
            &account_user.key,
            &account_mint.key,
            &account_spl.key,
        ),
        accounts,
    )?;
    solana_program::program::invoke_signed(
        &spl_token_2022::instruction::transfer_checked(
            &account_spl.key,
            &account_mana_spla.key,
            &account_mint.key,
            &account_user_spla.key,
            &account_mana_auth.key,
            &[],
            5000000000,
            9,
        )?,
        accounts,
        &[&[&[], &[account_mana_auth_calc.1]]],
    )?;

    Ok(())
}
